import json
from math import floor
from botocore.exceptions import ClientError
from datetime import datetime
from string import Template
from time import sleep
from unittest.mock import MagicMock
from pinthesky.database import MAX_ITEMS

from pinthesky.globals import app_context


def test_job_operations(jobs, groups, cameras):
    from pinthesky.resource.jobs import JOB_TYPES

    iot_client = MagicMock()
    app_context.inject('iot', iot_client, force=True)

    assert jobs().body == {
        'items': [],
        'nextToken': None
    }

    assert jobs(method="POST", body={}).code == 400
    assert jobs(method="POST", body={'type': 'farts'}).code == 400
    assert jobs(method="POST", body={'type': 'reboot'}).code == 400

    # Create a test group and associate some cameras
    assert groups(method="POST", body={'name': 'Home'}).code == 200
    assert groups('/Home/cameras', method="POST", body={
        'cameras': ['first', 'second']
    }).code == 204

    tracking = {}

    def create_job(jobId, targets, document, description, **kwargs):
        tracking[jobId] = document
        assert kwargs['jobExecutionsRetryConfig'] == {
            'criteriaList': [
                {
                    'failureType': 'FAILED',
                    'numberOfRetries': 2
                }
            ]
        }
        assert targets == [
            'arn:aws:iot:us-east-1:123456789012:thing/first',
            'arn:aws:iot:us-east-1:123456789012:thing/second'
        ]
        return {
            'jobId': jobId,
            'description': description
        }

    iot_client.create_job = MagicMock()
    iot_client.create_job.side_effect = create_job

    create = jobs(method="POST", body={'type': 'reboot', 'groups': ['Home']})
    sleep(1)
    create_up = jobs(
        method="POST",
        body={'type': 'update', 'description': '', 'cameras': ['first', 'second']}
    )
    create_logs = jobs(
        method="POST",
        body={'type': 'service-logs', 'description': '', 'cameras': ['first', 'second'], 'parameters': {'lines': 20, 'service': 'pinthesky', 'user': 'root'}}
    )
    assert create.code == 200
    assert create_up.code == 200
    assert create_logs.code == 200
    assert create.body['jobId'] in tracking
    reboot_template = Template(JOB_TYPES['reboot'])
    reboot_doc = reboot_template.safe_substitute(user='root')
    assert reboot_doc == tracking[create.body['jobId']]

    assert json.loads(reboot_doc) == {
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
                    "runAsUser": "root"
                }
            }
        ]
    }

    assert json.loads(tracking[create_up.body['jobId']]) == {
        "_comment": "Updates the Pi In The Sky Device software",
        "version": "1.0",
        "steps": [
            {
                "action": {
                    "name": "Stop Service",
                    "type": "runHandler",
                    "input": {
                        "handler": "stop-services.sh",
                        "args": ["pinthesky"],
                        "path": "default"
                    },
                    "runAsUser": "root"
                }
            },
            {
                "action": {
                    "name": "Upgrade Software",
                    "type": "runHandler",
                    "input": {
                        "handler": "upgrade-pinthesky.sh",
                        "args": ["$version"],
                        "path": "default"
                    },
                    "runAsUser": "root"
                }
            },
            {
                "action": {
                    "name": "Start Service",
                    "type": "runHandler",
                    "input": {
                        "handler": "start-services.sh",
                        "args": ["pinthesky"],
                        "path": "default"
                    },
                    "runAsUser": "root"
                }
            }
        ]
    }

    assert jobs().body['items'][2] == create.body

    assert jobs('/farts').code == 404

    assert cameras('/first/jobs').body['items'][2] == create.body
    assert cameras('/second/jobs').body['items'][2] == create.body

    assert jobs('/farts/executions').code == 404

    def list_job_executions(jobId, maxResults, nextToken=None):
        assert maxResults == MAX_ITEMS
        assert jobId == create.body['jobId']
        assert nextToken is None
        return {
            'executionSummaries': [
                {
                    'thingArn': 'arn:aws:iot:us:012345678912:thing/first',
                    'jobExecutionSummary': {
                        'status': 'QUEUED',
                        'executionNumber': 123,
                        'queuedAt': datetime.now(),
                        'startedAt': datetime.now(),
                        'lastUpdatedAt': datetime.now(),
                    }
                }
            ]
        }

    iot_client.list_job_executions_for_job = MagicMock()
    iot_client.list_job_executions_for_job.side_effect = list_job_executions

    url = f'/{create.body["jobId"]}/executions'
    assert jobs(url).body['items'][0]['thingName'] == 'first'

    def describe_job(jobId):
        assert jobId in tracking
        return {
            'job': {
                'status': 'COMPLETED',
                'description': 'A something job'
            }
        }

    iot_client.describe_job = MagicMock()
    iot_client.describe_job.side_effect = describe_job

    assert jobs(f'/{create.body["jobId"]}').body == {
        **create.body,
        'status': 'COMPLETED',
        'description': 'A something job'
    }

    queued_at = datetime.now()

    def describe_job_execution(jobId, thingName, executionNumber=None):
        if thingName == 'farts':
            raise ClientError({
                'Error': {
                    'Code': 'ResourceNotFoundException'
                }
            }, 'DescribeJobExecution')
        thing_arn = f'arn:aws:iot:us-east-1:123456789012:thing/{thingName}'
        number = executionNumber if executionNumber is not None else 1
        return {
            'execution': {
                'jobId': jobId,
                'status': 'FAILED',
                'queuedAt': queued_at,
                'thingArn': thing_arn,
                'executionNumber': number
            }
        }

    iot_client.describe_job_execution = MagicMock()
    iot_client.describe_job_execution.side_effect = describe_job_execution

    assert jobs(f'/{create.body["jobId"]}/executions/farts').code == 404
    assert jobs(f'/{create.body["jobId"]}/executions/first', query_params={'executionId': 2}).body == {
        'jobId': create.body["jobId"],
        'status': 'FAILED',
        'queuedAt': floor(queued_at.timestamp()),
        'executionNumber': 2,
        'thingName': 'first'
    }

    iot_client.update_job = MagicMock()
    iot_client.cancel_job = MagicMock()

    assert jobs('/farts', method="PUT", body={}).code == 404
    updated = jobs(f'/{create.body["jobId"]}/cancel', method="POST", body={
        'comment': 'This job sucks, killing it'
    })
    assert updated.body['status'] == 'CANCELED'
    iot_client.cancel_job.assert_called_once()

    assert jobs(f'/{create.body["jobId"]}', method="PUT", body={
        'description': 'This is an updated job'
    }).code == 200
    iot_client.update_job.assert_called_once()

    def cancel_job_execution(jobId, thingName, **kwargs):
        if thingName == 'farts':
            raise ClientError({
                'Error': {
                    'Code': 'ResourceNotFoundException'
                }
            }, 'CancelJobExecution')
        if jobId == 'farts':
            raise ClientError({
                'Error': {
                    'Code': 'InternalServerException'
                }
            }, 'CancelJobExecution')



    iot_client.cancel_job_execution = MagicMock()
    iot_client.cancel_job_execution.side_effect = cancel_job_execution
    assert jobs(f'/{create.body["jobId"]}/executions/first/cancel', method='POST', body={
        'force': True,
    }).code == 200
    
    assert jobs(f'/{create.body["jobId"]}/executions/farts/cancel', method='POST').code == 404
    assert jobs('/farts/executions/first/cancel', method='POST').code == 500

    iot_client.delete_job_execution = MagicMock()
    assert jobs(f'/{create.body["jobId"]}/executions/first/number/1', method='DELETE').code == 204
    iot_client.delete_job_execution.assert_called_once()

    iot_client.delete_job = MagicMock()

    jobs(f'/{create.body["jobId"]}', method="DELETE")
    iot_client.delete_job.assert_called_once()
    assert jobs(f'/{create.body["jobId"]}').code == 404
