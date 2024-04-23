import boto3
import logging
from botocore.exceptions import ClientError
from ophis.globals import app_context, request, response
from pinthesky.database import DataSessions, DataConnections
from pinthesky.resource.helpers import create_query_params
from pinthesky import api


logger = logging.getLogger(__name__)


app_context.inject('connections', DataConnections())
app_context.inject('sessions', DataSessions())


@api.route('/connections')
def list_connections(connections):
    resp = connections.items(
        request.account_id(),
        params=create_query_params(request=request)
    )

    return {
        'items': resp.items,
        'nextToken': resp.next_token,
    }


@api.route('/connections/:connectionId')
def get_connection(connectionId, connections):
    resp = connections.get(
        request.account_id(),
        item_id=connectionId,
    )
    if resp is None:
        response.status_code = 404
        return {
            'message': f'Connection {connectionId} was not found'
        }
    return resp


@api.route('/connections/:connectionId', methods=['DELETE'])
def delete_connection(connectionId, connections):
    resp = get_connection(connectionId, connections)
    if response.status_code == 404:
        response.status_code = 204
        return
    management = boto3.client(
        'apigatewaymanagementapi',
        endpoint_url=resp['managementEndpoint'])
    try:
        management.delete_connection(
            ConnectionId=connectionId,
        )
        logger.info(f'Successfully disconnected {connectionId}')
    except ClientError as e:
        if e.response['Error']['Code'] == 'GoneException':
            logger.warning(f"Connection {connectionId} is already gone")
        else:
            raise
    response.status_code = 204


@api.route('/connections/:connectionId/sessions')
def list_sessions(connectionId, connections, sessions):
    resp = get_connection(connectionId, connections)
    if response.status_code == 404:
        return resp
    resp = sessions.items(
        request.account_id(),
        'Connections',
        resp['connectionId'],
        params=create_query_params(request)
    )
    return {
        'items': resp.items,
        'nextToken': resp.next_token,
    }


@api.route('/connections/:connectionId/sessions/:invokeId')
def get_session(connectionId, invokeId, connections, sessions):
    resp = get_connection(connectionId, connections)
    if response.status_code == 404:
        return resp
    resp = sessions.get(
        request.account_id(),
        'Connections',
        resp['connectionId'],
        item_id=invokeId,
    )
    if resp is None:
        response.status_code = 404
        return {
            'message': f'Session for {connectionId}:{invokeId} was not found'
        }
    return resp
