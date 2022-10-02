import json
from datetime import datetime
from string import Template
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
    }).code == 200

    tracking = {}

    def create_job(jobId, targets, document, description):
        tracking[jobId] = document
        assert targets == ['first', 'second']
        return {
            'jobId': jobId,
            'description': description
        }

    iot_client.create_job = MagicMock()
    iot_client.create_job.side_effect = create_job

    create = jobs(method="POST", body={'type': 'reboot', 'groups': ['Home']})
    assert create.code == 200
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
                        "handler": "reboot.sh"
                    },
                    "runAsUser": "root"
                }
            }
        ]
    }

    assert jobs().body['items'][0] == create.body

    assert cameras('/first/jobs').body['items'][0] == create.body
    assert cameras('/second/jobs').body['items'][0] == create.body

    assert jobs('/farts/executions').code == 404

    def list_job_executions(jobId, maxResults, nextToken=None):
        assert maxResults == MAX_ITEMS
        assert jobId == create.body['jobId']
        assert nextToken is None
        return {
            'executionSummaries': [
                {
                    'thingArn': 'arn:aws:iot:us:012345678912:thing:first',
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