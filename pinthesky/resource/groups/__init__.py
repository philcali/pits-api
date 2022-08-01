import json
from pinthesky import api
from pinthesky.database import Groups, GroupsToCameras, QueryParams, MAX_ITEMS, Repository
from pinthesky.exception import ConflictException
from pinthesky.globals import app_context, request, response


app_context.inject('group_data', Groups())
app_context.inject('group_camera_data', GroupsToCameras())


@api.route("/groups/:thing_name/cameras")
def list_group_cameras(group_camera_data, thing_name):
    limit = int(request.queryparams.get('limit', MAX_ITEMS))
    limit = min(MAX_ITEMS, max(1, limit))
    next_token = request.queryparams.get('nextToken', None)
    page = group_camera_data.items(
        request.account_id(),
        thing_name,
        params=QueryParams(limit=limit, next_token=next_token))
    return {
        'items': page.items,
        'nextToken': page.next_token
    }


@api.route("/groups/:group_name/cameras", methods=['POST'])
def create_group_cameras(camera_group_data, group_camera_data, group_name):
    input = json.loads(request.body)
    updates = []
    for thing_name in input["cameras"]:
        updates.append({
            'repository': group_camera_data,
            'parent_ids': [group_name],
            'item': {
                'id': thing_name
            }
        })
        updates.append({
            'repository': camera_group_data,
            'parent_ids': [thing_name],
            'item': {
                'id': group_name
            }
        })
    Repository.batch_write(request.account_id(), updates=updates)


@api.route("/groups/:group_name/cameras/:thing_name", methods=['DELETE'])
def delete_group_camera(
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


@api.route("/groups", methods=['POST'])
def create_group(group_data):
    group = json.loads(request.body)
    if "name" not in group:
        response.status_code = 400
        return {
            'message': 'Group requires name to be set.'
        }
    try:
        return group_data.create(request.account_id(), item=group)
    except ConflictException as e:
        response.status_code = 409
        return {
            'message': str(e)
        }


@api.route("/groups/:group_name")
def get_group(group_data, group_name):
    group = group_data.get(request.account_id(), item_id=group_name)
    if group is None:
        response.status_code = 404
        return {
            'message': f'Group with name {group_name} does not exist.'
        }
    else:
        return group


@api.route("/groups/:group_name", methods=['DELETE'])
def delete_group(
        group_data,
        camera_group_data,
        group_camera_data,
        group_name):
    truncated = True
    next_token = None
    updates = [{
        'repository': group_data,
        'item': {
            'name': group_name
        },
        'delete': True
    }]
    while truncated:
        page = group_camera_data.items(
            request.account_id(),
            group_name,
            params=QueryParams(limit=MAX_ITEMS, next_token=next_token))
        for item in page.items:
            updates.append({
                'repository': group_camera_data,
                'parent_ids': [group_name],
                'item': {
                    'id': item['id']
                },
                'delete': True
            })
            updates.append({
                'repository': camera_group_data,
                'parent_ids': [item['id']],
                'item': {
                    'id': group_name
                },
                'delete': True
            })
        next_token = page.next_token
        truncated = next_token is not None
    Repository.batch_write(request.account_id(), updates=updates)


@api.route("/groups/:group_name", methods=['PUT'])
def put_group(group_data, group_name):
    group = json.loads(request.body)
    group['name'] = group_name
    return group_data.update(request.account_id(), item=group)


@api.route("/groups")
def list_groups(group_data):
    limit = int(request.queryparams.get('limit', MAX_ITEMS))
    limit = min(MAX_ITEMS, max(1, limit))
    next_token = request.queryparams.get('next_token', None)
    page = group_data.items(
        request.account_id(),
        params=QueryParams(limit=limit, next_token=next_token))
    return {
        'items': page.items,
        'nextToken': page.next_token
    }
