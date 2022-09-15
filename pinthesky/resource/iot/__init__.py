import boto3
import os
from pinthesky import api
from pinthesky.globals import app_context, request
from pinthesky.resource.helpers import get_limit


DATA_ENDPOINT = f'https://{os.getenv("DATA_ENDPOINT")}'


app_context.inject('iot', boto3.client('iot'))
app_context.inject('s3', boto3.client('s3'))
app_context.inject(
    name='iot_data',
    value=boto3.client('iot-data', endpoint_url=DATA_ENDPOINT))


@api.route("/iot/groups")
def list_iot_groups(iot):
    next_token = request.queryparams.get('nextToken', None)
    kwargs = {'maxResults': get_limit(request)}
    if next_token is not None:
        kwargs['nextToken'] = next_token
    response = iot.list_thing_groups(**kwargs)
    return {
        'nextToken': response.get('nextToken', None),
        'items': response.get('thingGroups', [])
    }


@api.route("/iot/groups/:group_name/things")
def list_iot_things_in_group(iot, group_name):
    next_token = request.queryparams.get('nextToken', None)
    kwargs = {
        'maxResults': get_limit(request),
        'thingGroupName': group_name
    }
    if next_token is not None:
        kwargs['nextToken'] = next_token
    response = iot.list_things_in_thing_group(**kwargs)
    return {
        'nextToken': response.get('nextToken', None),
        'items': response.get('things', [])
    }
