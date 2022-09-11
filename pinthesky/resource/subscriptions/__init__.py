import boto3
import json
from botocore.exceptions import ClientError
from pinthesky.database import Subscriptions
from pinthesky.globals import app_context, request, response
from pinthesky.resource import api
from pinthesky.resource.helpers import create_query_params

app_context.inject('subscription_data', Subscriptions())
app_context.inject('sns', boto3.resource('sns'))


@api.route('/subscriptions')
def list_subscriptions(subscription_data):
    page = subscription_data.items(
        request.account_id(),
        request.username(),
        params=create_query_params(request))
    return {
        'items': page.items,
        'nextToken': page.next_token
    }


@api.route('/subscriptions/:id')
def get_subscription(subscription_data, sns, id):
    sub_data = subscription_data.get(
        request.account_id(),
        request.username(),
        item_id=id)
    resp_data = {}
    if sub_data is not None:
        subscriber = sns.Subscription(arn=sub_data['arn'])
        try:
            attrs = subscriber.attributes
            if 'FilterPolicy' in attrs:
                resp_data['filter'] = json.loads(attrs['FilterPolicy'])
            resp_data['id'] = sub_data['id']
            resp_data['protocol'] = sub_data['protocol']
            resp_data['endpoint'] = sub_data['endpoint']
        except ClientError as e:
            if e.response['Error']['Code'] != 'NotFound':
                raise
    if 'id' not in resp_data:
        response.status_code = 404
        return {'message': f'Subscription {id} does not exist.'}
    return resp_data


@api.route('/subscriptions', methods=['POST'])
def create_subscription(subscription_data, sns, topic_arn):
    data = json.loads(request.body)
    topic = sns.Topic(arn=topic_arn)
    params = {
        'Protocol': data['protocol'],
        'Endpoint': data['endpoint'],
        'ReturnSubscriptionArn': True
    }
    if 'filter' in data:
        params['Attributes'] = {'FilterPolicy': json.dumps(data['filter'])}
    subscriber = topic.subscribe(**params)
    return subscription_data.create(
        request.account_id(),
        request.username(),
        item={
            'protocol': data['protocol'],
            'endpoint': data['endpoint'],
            'arn': subscriber.arn,
            'id': subscriber.arn.replace(topic_arn + ":", ""),
        })


@api.route('/subscriptions/:id', methods=['PUT'])
def put_subscription(subscription_data, sns, id):
    data = json.loads(request.body)
    sub_data = subscription_data.get(
        request.account_id(),
        request.username(),
        item_id=id)
    resp_data = {}
    if sub_data is not None:
        subscriber = sns.Subscription(arn=sub_data['arn'])
        filter_policy = json.dumps(data.get('filter', {}))
        try:
            subscriber.set_attributes(
                AttributeName="FilterPolicy",
                AttributeValue=filter_policy)
            resp_data['protocol'] = sub_data['protocol']
            resp_data['endpoint'] = sub_data['endpoint']
            resp_data['id'] = sub_data['id']
            resp_data['filter'] = data.get('filter', {})
        except ClientError as e:
            if e.response['Error']['Code'] != 'NotFound':
                raise
    if 'id' not in resp_data:
        response.status_code = 404
        return {
            'message': f'Subscription {sub_data.id} does not exist.'
        }
    return resp_data


@api.route('/subscriptions/:id', methods=['DELETE'])
def delete_subscription(subscription_data, sns, id):
    sub_data = subscription_data.get(
        request.account_id(),
        request.username(),
        item_id=id)
    if sub_data is not None:
        subscriber = sns.Subscription(arn=sub_data['arn'])
        subscriber.delete()
        subscription_data.delete(
            request.account_id(),
            request.username(),
            item_id=id)
