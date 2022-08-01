import json
from pinthesky import api
from pinthesky.database import Configurations
from pinthesky.globals import app_context, request, response


app_context.inject('config_data', Configurations())


@api.route("/configurations/default")
def get_configuration(config_data):
    default_item = config_data.get_default(request.account_id())
    if default_item is None:
        response.status_code = 404
        return {
            'message': 'The default configuration data is not found'
        }
    else:
        return default_item


@api.route("/configurations/default", methods=['PUT'])
def put_configuration(config_data):
    item = json.loads(request.body)
    item['id'] = 'default'
    return config_data.put(request.account_id(), item)
