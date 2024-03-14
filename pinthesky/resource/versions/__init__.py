from pinthesky.database import Versions
from pinthesky.resource import api
from pinthesky.globals import app_context, request, response
from pinthesky.resource.helpers import create_query_params

app_context.inject('version_data', Versions())


@api.route("/versions")
def list_versions(version_data):
    page = version_data.items(
        request.account_id(),
        params=create_query_params(request, sort_order='descending'),
    )
    return {
        'items': page.items,
        'nextToken': page.next_token,
    }


@api.route("/versions/latest")
def get_latest(version_data):
    latest = version_data.get(
        request.account_id(),
        'latest',
        item_id="current")
    if latest is None:
        response.status_code = 404
        return {
            'message': 'Latest version is not found',
        }
    latest['name'] = latest['tag']
    del latest['tag']
    return latest
