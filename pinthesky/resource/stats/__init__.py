from pinthesky.database import DeviceHealth
from pinthesky.resource import api
from pinthesky.globals import app_context, request
from pinthesky.resource.helpers import create_query_params

app_context.inject('stats_data', DeviceHealth())


@api.route('/stats', methods=['GET'])
def list_latest(stats_data):
    page = stats_data.items(
        request.account_id(),
        'latest',
        params=create_query_params(request)
    )
    return {
        'items': page.items,
        'nextToken': page.next_token
    }
