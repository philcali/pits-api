from collections import namedtuple
from datetime import datetime
from string import Template
from botocore.exceptions import ClientError
from pinthesky import api
from pinthesky.globals import app_context
from unittest.mock import MagicMock
import json
import pytest


Response = namedtuple('Response', field_names=['code', 'body', 'headers'])


class Resources():
    def __init__(self, module) -> None:
        self.module = module
        self.resource_name = module.__name__.split('.')[-1]

    def __call__(self, *args, **kwds):
        return self.request('/'.join(args), **kwds)

    def request(self, name="", method='GET', query_params={}, body=None):
        path = f'/{self.resource_name}{name}'
        with open('events/resources/request.template.json') as f:
            content = f.read()
            template = Template(content)
            event = json.loads(template.safe_substitute(
                path=path,
                method=method,
                body=json.dumps(json.dumps(body)) if body is not None else '""'
            ))
            event['queryStringParameters'] = query_params
        res = api(event=event, context={})
        return Response(
            code=res['statusCode'],
            body=json.loads(res['body']) if res['body'] is not None else "",
            headers=res['headers']
        )


@pytest.fixture(scope="module")
def cameras(table):
    assert table.name == 'Pits'
    from pinthesky.resource import cameras

    iot = MagicMock()
    iot_data = MagicMock()

    def side_effect(Bucket, Key):
        if Key == 'images/PitsCamera1/thumbnail_latest.jpg':
            return {
                'ContentType': 'text/plain',
                'ContentLength': 100,
                'LastModified': datetime.now()
            }
        else:
            raise ClientError({
                'Error': {
                    'Code': '404'
                }
            }, 'head_object')
    s3 = MagicMock()
    s3.head_object = MagicMock()
    s3.head_object.side_effect = side_effect
    app_context.inject('iot', iot, force=True)
    app_context.inject('iot_data', iot_data, force=True)
    app_context.inject('s3', s3, force=True)
    return Resources(cameras)


def test_camera_crud_workflow(cameras):
    # List, confirm empty
    assert cameras.request().body == {
        'items': [],
        'nextToken': None
    }

    # Create new
    created_camera = cameras.request(method='POST', body={
        'thingName': 'PitsCamera1',
        'displayName': 'Living Room Camera',
        'description': 'This is living room.'
    })

    assert created_camera.code == 200
    cam1 = created_camera.body
    assert 'createTime' in cam1
    assert 'updateTime' in cam1
    assert cam1['thingName'] == 'PitsCamera1'
    assert cam1['displayName'] == 'Living Room Camera'

    # Results in a conflict
    assert cameras(method='POST', body=cam1).code == 409

    # Reads, gets the sane value
    assert cameras(f'/{cam1["thingName"]}').body == cam1

    # shows up in list
    assert cam1 in cameras().body['items']

    # Update is allowed
    assert cameras(
        f'/{cam1["thingName"]}',
        method='PUT',
        body=cam1
    ).code == 200

    for index in range(2, 10):
        cameras(method='POST', body={
            'thingName': f'PitsCamera{index}',
        })

    # Batch get support
    thing_names = [f'PitsCamera{n}' for n in [3, 6, 9]]
    params = {'thingName': ','.join(thing_names)}
    batch_get = cameras(query_params=params)
    assert batch_get.body['items'] == [
        cameras(f'/{thing_names[0]}').body,
        cameras(f'/{thing_names[2]}').body,
        cameras(f'/{thing_names[1]}').body
    ]

    # Paginate
    full_list = cameras().body['items']
    concat_list = []
    pages = 0
    next_token = None
    truncated = True
    while truncated:
        pages += 1
        params = {'limit': 4, 'nextToken': next_token}
        page = cameras.request(query_params=params)
        next_token = page.body['nextToken']
        concat_list += page.body['items']
        truncated = next_token is not None
    assert pages == 3
    assert concat_list == full_list

    # Send a capture request
    assert cameras(
        f'/{cam1["thingName"]}/captureImage',
        method='POST'
    ).code == 200

    assert cameras('/PitsCamera1/captureImage').code == 200
    assert cameras('/PitsCamera2/captureImage').code == 404

    # Send a health request
    assert cameras(
        f'/{cam1["thingName"]}/stats',
        method='POST'
    ).code == 200

    # Removal
    cameras(f'/{cam1["thingName"]}', method='DELETE')
    assert cameras(f'/{cam1["thingName"]}').code == 404
