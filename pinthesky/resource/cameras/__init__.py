import json
import re
from botocore.exceptions import ClientError
from pinthesky import api
from pinthesky.conversion import timestamp_to_motion
from pinthesky.database import Cameras, CamerasToGroups, QueryParams, Repository
from pinthesky.exception import ConflictException
from pinthesky.globals import app_context, request, response
from pinthesky.resource.helpers import create_query_params, get_limit


app_context.inject('camera_data', Cameras())
app_context.inject('camera_group_data', CamerasToGroups())


@api.route("/cameras")
def list_cameras(camera_data):
    thing_names = request.queryparams.get('thingName', None)
    if thing_names is None:
        page = camera_data.items(
            request.account_id(),
            params=create_query_params(request))
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
            reads=[
                {'id': item_id, 'repository': camera_data}
                for item_id in item_ids
            ]
        )
    }


@api.route("/cameras/:thing_name")
def get_camera(camera_data, thing_name):
    camera = camera_data.get(request.account_id(), item_id=thing_name)
    if camera is None:
        response.status_code = 404
        return {
            'message': f'Camera with thing name {thing_name} does not exist.'
        }
    else:
        return camera


@api.route("/cameras/:thing_name/groups")
def list_camera_groups(camera_group_data, thing_name):
    page = camera_group_data.items(
        request.account_id(),
        thing_name,
        params=create_query_params(request))
    return {
        'items': page.items,
        'nextToken': page.next_token
    }


@api.route('/cameras/:thing_name/videos')
def list_camera_videos(motion_videos_data, thing_name):
    page = motion_videos_data.items(
        request.account_id(),
        thing_name,
        params=create_query_params(
            request=request,
            sort_order="descending",
            sort_field="motionVideo",
            format=timestamp_to_motion))
    return {
        'items': page.items,
        'nextToken': page.next_token
    }


@api.route('/camera/:thing_name/stats')
def list_device_health_history(stats_data, thing_name):
    page = stats_data.items(
        request.account_id(),
        thing_name,
        params=create_query_params(
            request=request,
            sort_order='descending',
            sort_field='SK',
            format=str
        )
    )
    return {
        'items': page.items,
        'nextToken': page.next_token
    }


@api.route('/cameras/:thing_name/stats/:timestamp')
def get_health_entry(stats_data, thing_name, timestamp):
    rval = stats_data.get(request.account_id(), thing_name, item_id=timestamp)
    if rval is None:
        response.status_code = 404
        return {
            'message': f'No entry for {thing_name} at {timestamp}.'
        }
    return rval


@api.route("/cameras/:thing_name/groups", methods=['POST'])
def create_camera_groups(camera_group_data, group_camera_data, thing_name):
    input = json.loads(request.body)
    updates = []
    for group_name in input["groups"]:
        updates.append({
            'repository': camera_group_data,
            'parent_ids': [thing_name],
            'item': {
                'id': group_name
            }
        })
        updates.append({
            'repository': group_camera_data,
            'parent_ids': [group_name],
            'item': {
                'id': thing_name
            }
        })
    Repository.batch_write(request.account_id(), updates=updates)


@api.route("/cameras/:thing_name/groups/:group_name", methods=['DELETE'])
def delete_camera_group(
        camera_group_data,
        group_camera_data,
        thing_name,
        group_name):
    updates = []
    updates.append({
        'repository': camera_group_data,
        'parent_ids': [thing_name],
        'item': {
            'id': group_name
        },
        'delete': True
    })
    updates.append({
        'repository': group_camera_data,
        'parent_ids': [group_name],
        'item': {
            'id': thing_name
        },
        'delete': True
    })
    Repository.batch_write(request.account_id(), updates=updates)


@api.route("/cameras", methods=['POST'])
def create_camera(camera_data, iot):
    camera = json.loads(request.body)
    if "thingName" not in camera:
        response.status_code = 400
        return {
            'message': 'Camera requires thingName to be set'
        }
    try:
        iot.describe_thing(thingName=camera['thingName'])
        return camera_data.create(request.account_id(), item=camera)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            response.status_code = 404
            return {
                'message': f'Thing {camera["thingName"]} does not exist'
            }
        raise
    except ConflictException as e:
        response.status_code = 409
        return {
            'message': str(e)
        }


@api.route("/cameras/:thing_name", methods=['DELETE'])
def delete_camera(
        camera_data,
        camera_group_data,
        group_camera_data,
        thing_name):
    truncated = True
    next_token = None
    updates = [{
        'repository': camera_data,
        'item': {
            'thingName': thing_name
        },
        'delete': True
    }]
    while truncated:
        page = camera_group_data.items(
            request.account_id(),
            thing_name,
            params=QueryParams(next_token=next_token))
        for item in page.items:
            updates.append({
                'repository': camera_group_data,
                'parent_ids': [thing_name],
                'item': {
                    'id': item['id']
                },
                'delete': True
            })
            updates.append({
                'repository': group_camera_data,
                'parent_ids': [item['id']],
                'item': {
                    'id': thing_name
                },
                'delete': True
            })
        next_token = page.next_token
        truncated = next_token is not None
    Repository.batch_write(request.account_id(), updates=updates)


@api.route("/cameras/:thing_name", methods=['PUT'])
def update_camera(camera_data, thing_name):
    camera = json.loads(request.body)
    camera["thingName"] = thing_name
    return camera_data.update(request.account_id(), item=camera)
