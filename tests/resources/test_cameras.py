import json
from unittest.mock import MagicMock
from pinthesky.globals import app_context
from botocore.client import ClientError
from io import StringIO


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

    # Send a capture video request
    assert cameras(
        f'/{cam1["thingName"]}/captureVideo',
        method='POST',
        body={
            "durationInSeconds": 20
        }
    ).code == 200

    iot_data = MagicMock()
    app_context.inject('iot_data', iot_data, force=True)

    def get_thing_shadow(thingName, shadowName):
        if thingName == 'PitsCamera2':
            raise ClientError(error_response={
                'Code': 'ResourceNotFoundException'
            }, operation_name='get_thing_shadow')
        return {
            'payload': StringIO(initial_value=json.dumps({
                'state': {
                    'reported': {
                        'camera': {
                            'camera_field1': 1,
                            'camera_field2': 2
                        },
                        'cloudwatch': {
                            'enabled': True
                        }
                    },
                    'desired': {
                        'camera': {
                            'camera_field1': 2,
                            'camera_field2': 2
                        },
                        'cloudwatch': {
                            'enabled': False
                        },
                    }
                }
            }))
        }

    iot_data.get_thing_shadow.side_effect = get_thing_shadow

    configuration = cameras(f'/{cam1["thingName"]}/configuration')
    assert configuration.code == 200
    assert configuration.body == {
        'camera_field1': 1,
        'camera_field2': 2
    }
    configuration = cameras(
        f'/{cam1["thingName"]}/configuration',
        query_params={'state': 'reported,desired,creed'})
    assert configuration.code == 200
    assert configuration.body == {
        'reported': {
            'camera_field1': 1,
            'camera_field2': 2
        },
        'desired': {
            'camera_field1': 2,
            'camera_field2': 2
        }
    }
    configuration = cameras(
        f'/{cam1["thingName"]}/configuration',
        query_params={'document': 'camera,cloudwatch'})
    assert configuration.code == 200
    assert configuration.body == {
        'camera': {
            'camera_field1': 1,
            'camera_field2': 2
        },
        'cloudwatch': {
            'enabled': True
        }
    }
    configuration = cameras(
        f'/{cam1["thingName"]}/configuration',
        query_params={
            'document': 'camera,cloudwatch',
            'state': 'desired,reported,creed',
        })
    assert configuration.code == 200
    assert configuration.body == {
        'desired': {
            'camera': {
                'camera_field1': 2,
                'camera_field2': 2
            },
            'cloudwatch': {
                'enabled': False
            }
        },
        'reported': {
            'camera': {
                'camera_field1': 1,
                'camera_field2': 2
            },
            'cloudwatch': {
                'enabled': True
            }
        }
    }
    assert cameras('/PitsCamera2/configuration').code == 404

    def update_thing_shadow(thingName, shadowName, payload):
        if thingName == 'PitsCamera2':
            raise ClientError(error_response={
                'Code': 'ResourceNotFoundException'
            }, operation_name='get_thing_shadow')
        assert shadowName == 'pinthesky'
        return {
            'payload': StringIO(initial_value=payload.decode('utf-8'))
        }

    iot_data.update_thing_shadow.side_effect = update_thing_shadow

    configuration = cameras(
        f'/{cam1["thingName"]}/configuration',
        method='POST',
        body={
            'camera_field1': 1,
            'camera_field2': 2
        })
    assert configuration.code == 200
    assert configuration.body == {
        'camera_field1': 1,
        'camera_field2': 2
    }

    configuration = cameras(
        f'/{cam1["thingName"]}/configuration',
        method='POST',
        body={
            'camera': {
                'camera_field1': 1,
                'camera_field2': 2
            },
            'cloudwatch': {
                'enabled': True
            }
        })
    assert configuration.code == 200
    assert configuration.body == {
        'camera': {
            'camera_field1': 1,
            'camera_field2': 2
        },
        'cloudwatch': {
            'enabled': True
        }
    }

    assert cameras('/PitsCamera2/configuration', method='POST', body={
        'farts': True
    }).code == 404

    # Send a health request
    assert cameras(
        f'/{cam1["thingName"]}/stats',
        method='POST'
    ).code == 200

    # Removal
    cameras(f'/{cam1["thingName"]}', method='DELETE')
    assert cameras(f'/{cam1["thingName"]}').code == 404
