import json
import re
from uuid import uuid4
from botocore.exceptions import ClientError
from pinthesky import api
from pinthesky.conversion import timestamp_to_motion
from pinthesky.database import Cameras, CamerasToGroups, QueryParams, Repository
from pinthesky.exception import ConflictException
from pinthesky.globals import app_context, request, response
from pinthesky.resource.helpers import create_query_params, get_limit
from pinthesky.s3 import generate_presigned_url


LATEST_THUMBNAIL = "thumbnail_latest.jpg"
DEFAULT_VIDEO_DURATION = 30


app_context.inject('camera_data', Cameras())
app_context.inject('camera_group_data', CamerasToGroups())


def publish_event(iot_data, thing_name, payload):
    return iot_data.publish(
        topic=f'pinthesky/events/{thing_name}/input',
        payload=bytes(json.dumps(payload), encoding="utf8"))


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


@api.route('/cameras/:thing_name/stats')
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


@api.route("/cameras/:thing_name/captureImage", methods=["POST"])
def start_capture_image(iot_data, thing_name):
    capture_id = str(uuid4())
    publish_event(iot_data, thing_name, {
        "name": "capture_image",
        "context": {
            "file_name": LATEST_THUMBNAIL,
            "capture_id": capture_id
        }
    })
    return {
        "id": capture_id
    }


@api.route("/cameras/:thing_name/captureVideo", methods=["POST"])
def start_capture_video(iot_data, thing_name):
    capture_id = str(uuid4())
    body = json.loads(request.body) if request.body != "" else {}
    # When requested, we will default to a 30 second buffer.
    duration = DEFAULT_VIDEO_DURATION
    if "durationInSeconds" in body:
        duration = body['durationInSeconds']
    publish_event(iot_data, thing_name, {
        "name": "capture_video",
        "context": {
            "capture_id": capture_id,
            "duration": duration,
        }
    })
    return {
        "id": capture_id
    }


@api.route("/cameras/:thing_name/captureImage")
def get_captured_image(s3, bucket_name, image_prefix, thing_name):
    s3key = f'{image_prefix}/{thing_name}/{LATEST_THUMBNAIL}'
    try:
        resp = s3.head_object(Bucket=bucket_name, Key=s3key)
        return {
            "id": s3key,
            "contentType": resp['ContentType'],
            "contentLength": resp['ContentLength'],
            "lastModified": resp['LastModified'].isoformat()
        }
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            response.status_code = 404
            return {
                "message": "capture image is not available"
            }
        else:
            raise


@api.route("/cameras/:thing_name/captureImage/url")
def get_captured_image_url(s3, bucket_name, image_prefix, thing_name):
    s3key = f'{image_prefix}/{thing_name}/{LATEST_THUMBNAIL}'
    return generate_presigned_url(s3, bucket_name, s3key)


@api.route("/cameras/:thing_name/configuration")
def get_camera_configuration(iot_data, thing_name):
    try:
        thing_resp = iot_data.get_thing_shadow(
            thingName=thing_name,
            shadowName="pinthesky")
        payload = json.loads(thing_resp['payload'].read())
        state_param = request.queryparams.get('state', None)
        document_param = request.queryparams.get('document', None)
        if document_param is None:
            if state_param is None:
                return payload['state']['reported']['camera']
            else:
                rval = {}
                for state in re.split('\\s*,\\s*', state_param):
                    if state in payload['state']:
                        rval[state] = payload['state'][state]['camera']
                return rval
        documents = re.split('\\s*,\\s*', document_param)
        rval = {}
        if state_param is None:
            for document in documents:
                if document in payload['state']['reported']:
                    rval[document] = payload['state']['reported'][document]
        else:
            for state in re.split('\\s*,\\s*', state_param):
                if state not in payload['state']:
                    continue
                rval[state] = {}
                for document in documents:
                    if document in payload['state'][state]:
                        rval[state][document] = payload['state'][state][document]
        return rval
    except ClientError as e:
        if e.response['Code'] == 'ResourceNotFoundException':
            response.status_code = 404
            return {
                "message": f'Configuration does not exist for {thing_name}'
            }
        raise


@api.route("/cameras/:thing_name/configuration", methods=["POST"])
def update_camera_configuration(iot_data, thing_name):
    try:
        configuration = json.loads(request.body)
        payload = {
            'state': {
                'desired': {
                }
            }
        }
        # In order to be backwards compatible, if the payload
        # received does not contain a "camera" field, then we
        # assume that the configuration only applies to the camera
        # document. Otherwise we will update any subdocument
        # that targets the thing.
        keys = []
        if 'camera' not in configuration:
            payload['state']['desired']['camera'] = configuration
        else:
            keys = list(configuration.keys())
            payload['state']['desired'].update(configuration)
        thing_resp = iot_data.update_thing_shadow(
            thingName=thing_name,
            shadowName="pinthesky",
            payload=bytes(json.dumps(payload), encoding="utf8"))
        r_payload = json.loads(thing_resp['payload'].read())
        if len(keys) == 0:
            return r_payload['state']['desired']['camera']
        rval = {}
        for key in keys:
            rval[key] = r_payload['state']['desired'][key]
        return rval
    except ClientError as e:
        if e.response['Code'] == 'ResourceNotFoundException':
            response.status_code = 404
            return {
                'message': f'Thing {thing_name} does not exist'
            }
        raise


@api.route("/cameras/:thing_name/stats", methods=["POST"])
def start_camera_health(iot_data, thing_name):
    health_id = str(uuid4())
    # TODO: we can match this entry so it shows as pending on the console
    publish_event(iot_data, thing_name, {
        "name": "health",
        "context": {
            "health_id": health_id
        }
    })
    return {
        "id": health_id
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


@api.route('/cameras/:thing_name/jobs')
def list_jobs_for_camera(camera_job_data, thing_name, first_index):
    page = camera_job_data.items_index(
        request.account_id(),
        thing_name,
        index_name=first_index,
        params=create_query_params(
            request=request,
            sort_order="descending"
        )
    )
    return {
        'items': page.items,
        'next_token': page.next_token
    }


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
