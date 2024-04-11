import json
import time
from ophis.globals import app_context, request, response
from pinthesky.database import DataTokens
from pinthesky.resource import api
from pinthesky.resource.helpers import create_query_params
from math import floor
from uuid import uuid4


DEFAULT_TIMEOUT_SECONDS = 60
app_context.inject('data_tokens', DataTokens())


@api.route("/tokens")
def list_tokens(data_tokens):
    page = data_tokens.items(
        request.account_id(),
        params=create_query_params(request),
    )
    return {
        'items': page.items,
        'nextToken': page.next_token
    }


@api.route('/tokens/:token_id')
def get_token(token_id, data_tokens):
    token = data_tokens.get(request.account_id(), item_id=token_id)
    if token is None:
        response.status_code = 404
        return {
            'message': f'Token with id {token_id} was not found',
        }
    return token


@api.route('/tokens', methods=['POST'])
def create_token(data_tokens):
    input = {}
    if request.body is not None and request.body != "":
        input = json.loads(request.body)
    timeout = input.get('timeoutInSeconds', DEFAULT_TIMEOUT_SECONDS)
    expires_in = floor(time.time()) + (timeout * 1000)
    return data_tokens.create(
        request.account_id(),
        item={
            'id': str(uuid4()),
            'expiresIn': expires_in,
            'authorization': {
                'connectionId': None,
                'activated': False,
            }
        }
    )


@api.route('/tokens/:token_id', methods=['DELETE'])
def delete_token(data_tokens, token_id):
    data_tokens.delete(request.account_id(), item_id=token_id)
    response.status_code = 204
