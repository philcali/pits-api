from pinthesky.router import Router
from pinthesky.globals import request, response, app_context
import json
import os


api = Router()
app_context.inject("some_key", "some_value")


@api.filter()
def cors():
    if request.method() == 'OPTIONS':
        response.headers = {
            'access-control-allow-origin': '*',
            'access-control-allow-methods': 'GET, POST, PUT, DELETE',
            'access-control-allow-headers': ', '.join([
                'Content-Type',
                'Content-Length',
                'Authorization'
            ])
        }
        response.break_continuation()


@api.route("/")
def index(some_key):
    assert some_key == "some_value"
    return "Hello World"


@api.route("/other/path")
def other_path(some_key):
    assert some_key == "some_value"
    return "Hello World"


@api.route('/pets/:petId')
def get_pet(petId):
    return f'Hello World, {petId}'


@api.route('/pets/:petId', methods=['PUT', 'POST'])
def put_pet(petId):
    assert 'value1' == request.authorizer()['jwt']['claims']['claim1']
    pet = json.loads(request.body)
    assert pet['name'] == 'Pixie'
    return {
        'id': petId,
        'name': pet['name']
    }


@api.route('/pets/:petId', methods=['DELETE'])
def delete_pet(petId):
    assert petId == 'pixie'
    response.status_code = 204


def test_router():
    events = os.listdir('events')
    for test_event in events:
        print(test_event)
        with open(os.path.join('events', test_event)) as f:
            event = json.loads(f.read())
        assert event['response'] == api(event=event['event'], context={})
