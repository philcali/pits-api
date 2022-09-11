from pinthesky.database import DeviceHealth
from pinthesky.resource import api
from pinthesky.globals import app_context, request, response
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


@api.route('/stats/:thing_name', methods=['GET'])
def list_device_health_history(stats_data, thing_name):
    page = stats_data.items(
        request.account_id(),
        thing_name,
        params=create_query_params(
            request=request,
            sort_order='descending',
            sort_field='SK'
        )
    )
    return {
        'items': page.items,
        'nextToken': page.next_token
    }


@api.route('/stats/:thing_name/timestamp/:timestamp', methods=['GET'])
def get_health_entry(stats_data, thing_name, timestamp):
    rval = stats_data.get(request.account_id(), thing_name, item_id=timestamp)
    if rval is None:
        response.status_code = 404
        return {
            'message': f'No entry for {thing_name} at {timestamp}.'
        }
    return rval
