import json
from datetime import datetime
from math import floor
from string import Template
from time import time
from uuid import uuid4
from pinthesky.database import DeviceJobs, DeviceToJobs, QueryParams, Repository
from pinthesky.globals import app_context, request, response
from pinthesky.resource import api
from pinthesky.resource.helpers import create_query_params, get_limit


app_context.inject('job_data', DeviceJobs())
app_context.inject('camera_job_data', DeviceToJobs())


JOB_TYPES = {
    'reboot':
    """
{
    "_comment": "Reboot the Pi In The Sky Camera hardware",
    "version": "1.0",
    "steps": [
        {
            "action": {
                "name": "Reboot Camera",
                "type": "runHandler",
                "input": {
                    "handler": "reboot.sh"
                },
                "runAsUser": "$user"
            }
        }
    ]
}
    """,
    'update':
    """
{
    "_comment": "Updates the Pi In The Sky Device software",
    "version": "1.0",
    "steps": [
        {
            "action": {
                "name": "Stop Service",
                "type": "runHandler",
                "input": {
                    "handler": "stop-services.sh",
                    "args": [
                        "pinthesky"
                    ]
                },
                "runAsUser": "$user"
            },
        },
        {
            "action": {
                "name": "Upgrade Software",
                "type": "runHandler",
                "input": {
                    "handler": "upgrade-pinthesky.sh",
                    "args": [
                        "$version"
                    ]
                },
                "runAsUser": "$user"
            }
        },
        {
            "action": {
                "name": "Start Service",
                "type": "runHandler",
                "input": {
                    "handler": "start-services.sh",
                    "args": [
                        "pinthesky"
                    ]
                },
                "runAsUser": "$user"
            }
        }
    ]
}
    """
}


@api.route('/jobs')
def list_jobs(job_data, first_index):
    page = job_data.items_index(
        request.account_id(),
        index_name=first_index,
        params=create_query_params(
            request=request,
            sort_order="descending"
        )
    )
    return {
        'items': page.items,
        'nextToken': page.next_token
    }


@api.route('/jobs', methods=["POST"])
def create_job(iot, job_data, group_camera_data, camera_job_data):
    payload = json.loads(request.body)
    create_time = floor(time())
    job_id = str(uuid4())
    if 'type' not in payload or payload['type'] not in JOB_TYPES:
        response.status_code = 400
        return {
            'message': f'Invalid job type. Valid types are {JOB_TYPES.keys()}'
        }
    kwargs = {
        'jobId': job_id,
        'targets': payload.get('cameras', []),
        'description': payload.get('description', f'A {payload["type"]} job')
    }
    for group in payload.get('groups', []):
        truncated = True
        params = QueryParams()
        while truncated:
            page = group_camera_data.items(
                request.account_id(),
                group,
                params=params)
            for item in page.items:
                kwargs['targets'].append(item['id'])
            params = QueryParams(next_token=page.next_token)
            truncated = params.next_token is not None
    if len(kwargs['targets']) == 0:
        response.status_code = 400
        return {
            'message': 'Need to supply a camera or group of cameras.'
        }
    template = Template(JOB_TYPES[payload['type']])
    parameters = payload.get('parameters', {'user': 'root'})
    kwargs['document'] = template.safe_substitute(**parameters)
    resp = iot.create_job(**kwargs)
    item = {
        'jobId': resp['jobId'],
        'type': payload['type'],
        'parameters': parameters,
        'createTime': create_time,
        'updateTime': create_time,
    }
    updates = [{
        'repository': job_data,
        'item': {
            **item,
            'GS1-PK': job_data.make_hash_key(request.account_id())
        }
    }]
    for camera in kwargs['targets']:
        updates.append({
            'repository': camera_job_data,
            'parent_ids': [camera],
            'item': {
                **item,
                'GS1-PK': camera_job_data.make_hash_key(
                    request.account_id(),
                    camera
                )
            }
        })
    Repository.batch_write(request.account_id(), updates=updates)
    return item


@api.route('/jobs/:job_id/executions')
def list_job_executions(job_data, job_id, iot):
    job = job_data.get(request.account_id(), item_id=job_id)
    if job is None:
        response.status_code = 404
        return {
            'message': f'Job with id {job_id} does not exist.'
        }
    kwargs = {'jobId': job['jobId'], 'maxResults': get_limit(request)}
    next_token = request.queryparams.get('nextToken', None)
    if next_token is not None:
        kwargs['nextToken'] = next_token
    resp = iot.list_job_executions_for_job(**kwargs)
    items = []
    for summary in resp.get('executionSummaries', []):
        new_item = {}
        for k, v in summary['jobExecutionSummary'].items():
            if isinstance(v, datetime):
                v = floor(v.timestamp())
            new_item[k] = v
        items.append({
            **new_item,
            'thingName': summary['thingArn'].split(':')[-1],
        })
    return {
        'items': items,
        'nextToken': resp.get('nextToken', None)
    }
