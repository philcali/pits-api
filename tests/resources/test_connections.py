import boto3
from botocore.exceptions import ClientError
from ophis.globals import app_context
from unittest.mock import patch, MagicMock


def test_connections(connections):
    connection_db = app_context.resolve()['connections']
    session_db = app_context.resolve()['sessions']

    empty = connections()

    assert empty.body['items'] == []
    assert empty.code == 200

    created = connection_db.create(
        connections.account_id(),
        item={
            'connectionId': 'abc-123',
            'managementEndpoint': 'http://example.com',
        }
    )

    created_other = connection_db.create(
        connections.account_id(),
        item={
            'connectionId': 'efg-456',
            'managementEndpoint': 'http://example.com',
        }
    )

    assert connections().body['items'][0] == created
    assert connections('/' + created['connectionId']).body == created
    assert connections('/not-found').code == 404

    assert connections('/not-found/sessions').code == 404

    empty = connections('/' + created['connectionId'] + '/sessions')
    assert empty.body['items'] == []
    assert empty.code == 200
    assert connections('/' + created['connectionId'] + '/sessions/not-found').code == 404

    session = session_db.create(
        connections.account_id(),
        'Connections',
        created['connectionId'],
        item={
            'invokeId': 'efg-456',
        }
    )

    assert connections('/' + created['connectionId'] + '/sessions').body['items'][0] == session
    assert connections('/' + created['connectionId'] + '/sessions/' + session['invokeId']).body == session
    assert connections('/not-found', method='DELETE').code == 204

    management = MagicMock()
    management.delete_connection = MagicMock()
    with patch.object(boto3, 'client', return_value=management) as mock_client:
        assert connections('/' + created['connectionId'], method='DELETE').code == 204
        mock_client.assert_called_once()

    management.delete_connection.assert_called_once()

    def delete_connection(ConnectionId):
        if ConnectionId == 'abc-123':
            raise ClientError({
                'Error': {
                    'Code': 'GoneException'
                }
            }, 'ManagementApi:DeleteConnection')
        if ConnectionId == 'efg-456':
            raise ClientError({
                'Error': {
                    'Code': 'InternalServerError'
                }
            }, 'ManagementApi: DeleteConnection')

    management.delete_connection = delete_connection
    with patch.object(boto3, 'client', return_value=management) as mock_client:
        assert connections('/' + created['connectionId'], method='DELETE').code == 204
        assert connections('/' + created_other['connectionId'], method='DELETE').code == 500
