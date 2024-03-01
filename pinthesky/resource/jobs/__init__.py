import json
from datetime import datetime
from math import floor
from string import Template
from time import time
from uuid import uuid4
from botocore.exceptions import ClientError
from pinthesky.database import DeviceJobs, DeviceToJobs, QueryParams, Repository
from pinthesky.globals import app_context, request, response
from pinthesky.resource import api
from pinthesky.resource.helpers import create_query_params, get_limit


app_context.inject('job_data', DeviceJobs())
app_context.inject('camera_job_data', DeviceToJobs())


def _convert_cloud_to_dto(item):
    new_item = {}
    for k, v in item.items():
        if k == 'thingArn':
            continue
        if isinstance(v, datetime):
            v = floor(v.timestamp())
        new_item[k] = v
    return new_item


def _upsert_job_definition(job_data, job_id, verify_terminal, thunk, strip_fields=[]):
    job = job_data.get(request.account_id(), item_id=job_id)
    if job is None:
        response.status_code = 404
        return {
            'message': f'Job with id {job_id} does not exist.'
        }
    payload = json.loads(request.body)
    kwargs = {**payload, 'jobId': job_id}
    for field in strip_fields:
        if field in kwargs:
            del kwargs[field]
    item = {'jobId': job_id}
    if verify_terminal:
        item["status"] = "CANCELED"
    thunk(**kwargs)
    return job_data.update(request.account_id(), item=item)


JOB_TYPES = {
    'shutdown':
    """
{
    "_comment": "Shuts down the Pi In The Sky Camera hardware",
    "version": "1.0",
    "steps": [
        {
            "action": {
                "name": "Shutdown Camera",
                "type": "runHandler",
                "input": {
                    "handler": "shutdown.sh",
                    "path": "default"
                },
                "runAsUser": "$user"
            }
        }
    ]
}
    """,
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
                    "handler": "reboot.sh",
                    "path": "default"
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
                    ],
                    "path": "default"
                },
                "runAsUser": "$user"
            }
        },
        {
            "action": {
                "name": "Upgrade Software",
                "type": "runHandler",
                "input": {
                    "handler": "upgrade-pinthesky.sh",
                    "args": [
                        "$version"
                    ],
                    "path": "default"
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
                    ],
                    "path": "default"
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
    arn_parts = request.context.invoked_function_arn.split(':')
    arn_prefix = ':'.join([
        'arn',
        arn_parts[1],
        'iot',
        arn_parts[3],
        request.account_id(),
        'thing'
    ])
    if 'type' not in payload or payload['type'] not in JOB_TYPES:
        response.status_code = 400
        return {
            'message': f'Invalid type. Valid types: {list(JOB_TYPES.keys())}'
        }

    def thing_arn(thing_name):
        return f'{arn_prefix}/{thing_name}'
    kwargs = {
        'jobId': job_id,
        'targets': list(map(thing_arn, payload.get('cameras', []))),
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
                kwargs['targets'].append(thing_arn(item['id']))
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
    kwargs['jobExecutionsRetryConfig'] = payload.get('retryConfig', {
        'criteriaList': [
            {
                "failureType": "FAILED",
                "numberOfRetries": 2
            }
        ]
    })
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
        thing_name = camera.split('/')[-1]
        updates.append({
            'repository': camera_job_data,
            'parent_ids': [thing_name],
            'item': {
                **item,
                'GS1-PK': camera_job_data.make_hash_key(
                    request.account_id(),
                    thing_name
                )
            }
        })
    Repository.batch_write(request.account_id(), updates=updates)
    return item


@api.route('/jobs/:job_id')
def describe_job(job_data, job_id, iot):
    job = job_data.get(request.account_id(), item_id=job_id)
    if job is None:
        response.status_code = 404
        return {
            'message': f'Job with id {job_id} does not exist.'
        }
    resp = iot.describe_job(jobId=job_id)
    return {
        **job,
        'status': resp['job']['status'],
        'description': resp['job']['description']
    }


@api.route('/jobs/:job_id', methods=['PUT'])
def update_job(job_data, job_id, iot):
    return _upsert_job_definition(
        job_data=job_data,
        job_id=job_id,
        verify_terminal=False,
        strip_fields=[
            'createTime',
            'updateTime',
            'parameters',
            'type',
            'status',
        ],
        thunk=iot.update_job)


@api.route('/jobs/:job_id/cancel', methods=['POST'])
def cancel_job(job_data, job_id, iot):
    return _upsert_job_definition(
        job_data=job_data,
        job_id=job_id,
        verify_terminal=True,
        thunk=iot.cancel_job)


@api.route('/jobs/:job_id', methods=['DELETE'])
def delete_job(job_data, job_id, iot):
    iot.delete_job(jobId=job_id)
    job_data.delete(request.account_id(), item_id=job_id)


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
        new_item = _convert_cloud_to_dto(summary['jobExecutionSummary'])
        items.append({
            **new_item,
            'thingName': summary['thingArn'].split('/')[-1],
        })
    return {
        'items': items,
        'nextToken': resp.get('nextToken', None)
    }


@api.route('/jobs/:job_id/executions/:thing_name')
def describe_job_execution(job_id, thing_name, iot):
    kwargs = {'jobId': job_id, 'thingName': thing_name}
    if 'executionId' in request.queryparams:
        kwargs['executionNumber'] = int(request.queryparams['executionId'])
    try:
        execution = iot.describe_job_execution(**kwargs)
        return {
            **_convert_cloud_to_dto(execution['execution']),
            'thingName': thing_name
        }
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            response.status_code = 404
            return {
                'message': f'Job {job_id} does not exist for {thing_name}'
            }
        raise


@api.route('/jobs/:job_id/executions/:thing_name/number/:number', methods=['DELETE'])
def delete_job_execution(job_id, thing_name, number, iot):
    iot.delete_job_execution(
        jobId=job_id,
        thingName=thing_name,
        force=True,
        executionNumber=int(number))


@api.route('/jobs/:job_id/executions/:thing_name/cancel', methods=['POST'])
def cancel_job_execution(job_id, thing_name, iot):
    payload = {}
    if request.body != "":
        payload = json.loads(request.body)
    kwargs = {**payload, 'jobId': job_id, 'thingName': thing_name}
    try:
        iot.cancel_job_execution(**kwargs)
        return {
            'thingName': thing_name,
            'jobId': job_id,
        }
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            response.status_code = 404
            return {
                'message': f'Job {job_id} does not exist for {thing_name}'
            }
        raise
