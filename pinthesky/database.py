from asyncio.log import logger
from decimal import Decimal
from math import floor
from time import time
from collections import namedtuple
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from pinthesky.exception import ConflictException, NotFoundException
from pinthesky.globals import app_context
from pinthesky.token import EncryptedTokenMarshaller


MAX_ITEMS = 100
CON_CHECK_CODE = 'ConditionalCheckFailedException'

QueryParams = namedtuple(
    'QueryParams',
    field_names=['limit', 'next_token'],
    defaults=[100, None])
QueryResults = namedtuple(
    'QueryResults',
    field_names=['items', 'next_token'],
    defaults=[[], None])


class Repository():
    def __init__(
            self,
            type,
            table=None,
            fields_to_keys={},
            token_marshaller=EncryptedTokenMarshaller()) -> None:
        self.__table = table if table is not None else app_context.resolve('GLOBAL')['table']
        self.__type = type
        self.fields_to_keys = fields_to_keys
        self.tokens = token_marshaller

    def batch_write(*args, updates, table=None):
        if table is None:
            table = app_context.resolve('GLOBAL')['table']
        with table.batch_writer() as batch:
            for update in updates:
                if 'repository' not in update or 'item' not in update:
                    logger.warn(f'Update skipped to missing fields: {update}')
                    continue
                keys = list(args)
                if 'parent_ids' in update:
                    for parent_id in update.pop('parent_ids'):
                        keys.append(parent_id)
                dto = update['repository'].make_dto(
                    *keys,
                    item=update['item'],
                    time_fields=['create', 'update'])
                if update.get("delete", False):
                    batch.delete_item(Key={'PK': dto['PK'], 'SK': dto['SK']})
                else:
                    batch.put_item(Item=dto)

    def prune_dto(self, original):
        if original is None:
            return None
        rval = {}
        for key, value in original.items():
            if key in ['PK', 'SK']:
                continue
            if type(value) is Decimal:
                value = int(value)
            rval[key] = value
        return rval

    def make_dto(self, *args, item, time_fields=['create', 'update']):
        new_item = {
            'PK': self.make_hash_key(*args)
        }
        for key, value in item.items():
            new_item[key] = value
        for key, value in self.fields_to_keys.items():
            if key not in item:
                raise Exception(f'The {self.__type} item needs a {key} field')
            new_item[value] = item[key]
        for time_field in time_fields:
            if f'{time_field}Time' not in item:
                new_item[f'{time_field}Time'] = int(floor(time()))
        return new_item

    def __encrypt_token(self, hash_key, res):
        return self.tokens.encrypt(
            hash_key=hash_key,
            header=':'.join([self.__type, 'next_token']),
            last_key=res.get('LastEvaluatedKey', None))

    def make_hash_key(self, *args):
        return ":".join([self.__type] + list(args))

    def items(self, *args, params=QueryParams()):
        hash_key = self.make_hash_key(*args)
        q_params = {
            'KeyConditionExpression': Key("PK").eq(hash_key),
            'Limit': params.limit
        }
        last_key = self.tokens.decrypt(
            hash_key=hash_key,
            header=':'.join([self.__type, 'next_token']),
            next_token=params.next_token)
        if last_key is not None:
            q_params['ExclusiveStartKey'] = last_key
        response = self.__table.query(**q_params)
        items = map(
            self.prune_dto,
            response['Items'] if 'Items' in response else [])
        return QueryResults(
            items=list(items),
            next_token=self.__encrypt_token(hash_key, response)
        )

    def create(self, *args, item):
        new_item = self.make_dto(*args, item=item)
        exp = "attribute_not_exists(PK) and attribute_not_exists(SK)"
        try:
            self.__table.put_item(
                Item=new_item,
                ConditionExpression=exp
            )
        except ClientError as e:
            if e.response['Error']['Code'] == CON_CHECK_CODE:
                raise ConflictException(
                    f'This {self.__type} item already exists.')
            raise e
        return self.prune_dto(new_item)

    def update(self, *args, item):
        new_item = self.make_dto(*args, item=item, time_fields=['update'])
        condition = "attribute_exists(PK) and attribute_exists(SK)"
        update_exp = []
        update_names = {}
        update_values = {}
        for key, value in new_item.items():
            if key in ['PK', 'SK'] or key in self.fields_to_keys:
                continue
            update_names[f'#{key}'] = key
            update_values[f':{key}'] = value
            update_exp.append(f'#{key} = :{key}')
        try:
            response = self.__table.update_item(
                Key={
                    'PK': new_item['PK'],
                    'SK': new_item['SK']
                },
                ConditionExpression=condition,
                UpdateExpression=f'SET {", ".join(update_exp)}',
                ExpressionAttributeNames=update_names,
                ExpressionAttributeValues=update_values,
                ReturnValues='ALL_NEW',
            )
            return self.prune_dto(response['Attributes'])
        except ClientError as e:
            if e.response['Error']['Code'] == CON_CHECK_CODE:
                raise NotFoundException(f'The {self.__type} item not exist.')
            raise e

    def delete(self, *args, item_id):
        self.__table.delete_item(
            Key={
                'PK': self.make_hash_key(*args),
                'SK': item_id
            }
        )

    def get(self, *args, item_id):
        response = self.__table.get_item(
            Key={
                'PK': self.make_hash_key(*args),
                'SK': item_id
            }
        )
        return self.prune_dto(response.get('Item', None))


class Configurations(Repository):
    def __init__(self, table=None) -> None:
        super().__init__(table=table, type="Configurations", fields_to_keys={
            'id': 'SK'
        })

    def get_default(self, account_id):
        return self.get(account_id, item_id='default')

    def put(self, account_id, item):
        try:
            return self.create(account_id, item=item)
        except ConflictException:
            return self.update(account_id, item=item)


class Groups(Repository):
    def __init__(self, table=None) -> None:
        super().__init__(table=table, type="Groups", fields_to_keys={
            'name': 'SK'
        })


class Cameras(Repository):
    def __init__(self, table=None) -> None:
        super().__init__(table=table, type="Cameras", fields_to_keys={
            'thingName': 'SK'
        })


class CamerasToGroups(Repository):
    def __init__(self, table=None) -> None:
        super().__init__(table=table, type="CamerasToGroups", fields_to_keys={
            'id': 'SK'
        })


class GroupsToCameras(Repository):
    def __init__(self, table=None) -> None:
        super().__init__(table=table, type="GroupsToCameras", fields_to_keys={
            'id': 'SK'
        })
