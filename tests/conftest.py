from collections import namedtuple
from pinthesky.globals import app_context
import pytest
import boto3
import subprocess

DynamoDBLocal = namedtuple('DynamoDBLocal', field_names=[
    'endpoint', 'process'
])


@pytest.fixture(scope="module")
def dynamodb_local():
    port = 8080
    proc = subprocess.Popen([
        "java", "-Djava.library.path=dynamodb/DynamoDBLocal_list",
        "-jar", "dynamodb/DynamoDBLocal.jar",
        "-port", f'{port}',
        "-inMemory"
    ])
    yield DynamoDBLocal(
        endpoint=f'http://localhost:{port}',
        process=proc
    )
    proc.kill()


@pytest.fixture(scope="module")
def dynamodb(dynamodb_local):
    return boto3.resource('dynamodb', endpoint_url=dynamodb_local.endpoint)


@pytest.fixture(scope="module")
def table(dynamodb):
    table = dynamodb.create_table(
        TableName='Pits',
        KeySchema=[
            {
                'AttributeName': 'PK',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'SK',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'PK',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'SK',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    table.wait_until_exists()
    app_context.inject('dynamodb', dynamodb)
    app_context.inject('table', table)
    yield table
    app_context.remove('dynamodb')
    app_context.remove('table')
