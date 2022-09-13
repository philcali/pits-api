import re
from pinthesky.database import DeviceHealth, Repository
from pinthesky.resource import api
from pinthesky.globals import app_context, request, response
from pinthesky.resource.helpers import create_query_params, get_limit

app_context.inject('stats_data', DeviceHealth())


@api.route('/stats')
def list_latest(stats_data):
    thing_names = request.queryparams.get('thingName', None)
    if thing_names is None:
        page = stats_data.items(
            request.account_id(),
            'latest',
            params=create_query_params(request)
        )
        return {
            'items': page.items,
            'nextToken': page.next_token
        }
    item_ids = re.split('\\s*,\\s*', thing_names)
    limit = get_limit(request)
    if len(item_ids) > limit:
        response.status_code = 400
        return {
            'message': f'Provided {len(item_ids)} is more than {limit}.'
        }
    return {
        'items': Repository.batch_read(
            request.account_id(),
            'latest',
            reads=[
                {'id': item_id, 'repository': stats_data}
                for item_id in item_ids
            ]
        )
    }
