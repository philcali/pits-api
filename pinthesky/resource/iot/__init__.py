import boto3
import json
import os
from uuid import uuid4
from botocore.exceptions import ClientError
from pinthesky import api
from pinthesky.database import MAX_ITEMS
from pinthesky.globals import app_context, request, response


DATA_ENDPOINT = f'https://{os.getenv("DATA_ENDPOINT")}'
LATEST_THUMBNAIL = "thumbnail_latest.jpg"


app_context.inject('iot', boto3.client('iot'))
app_context.inject('s3', boto3.client('s3'))
app_context.inject(
    name='iot_data',
    value=boto3.client('iot-data', endpoint_url=DATA_ENDPOINT))


def publish_event(iot_data, thing_name, payload):
    return iot_data.publish(
        topic=f'pinthesky/events/{thing_name}/input',
        payload=bytes(json.dumps(payload), encoding="utf8"))


@api.route("/iot/groups")
def list_iot_groups(iot):
    next_token = request.queryparams.get('nextToken', None)
    limit = int(request.queryparams.get('limit', MAX_ITEMS))
    limit = min(MAX_ITEMS, max(1, limit))
    kwargs = {'maxResults': limit}
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
    limit = int(request.queryparams.get('limit', MAX_ITEMS))
    limit = min(MAX_ITEMS, max(1, limit))
    kwargs = {'maxResults': limit, 'thingGroupName': group_name}
    if next_token is not None:
        kwargs['nextToken'] = next_token
    response = iot.list_things_in_thing_group(**kwargs)
    return {
        'nextToken': response.get('nextToken', None),
        'items': response.get('things', [])
    }


@api.route("/cameras/:thing_name/captureImage", methods=["POST"])
def start_capture_image(iot_data, thing_name):
    capture_id = uuid4()
    publish_event(iot_data, thing_name, {
        "name": "capture_image",
        "context": {
            "file_name": LATEST_THUMBNAIL,
            "capture_id": str(capture_id)
        }
    })
    return {
        "id": str(capture_id)
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
    expires_in = 3600
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': s3key},
        ExpiresIn=expires_in)
    return {
        'expiresIn': expires_in,
        'url': url
    }
