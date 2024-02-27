
def test_job_type_operations(jobTypes):
    assert jobTypes().body['items'][0] == {
        'name': 'shutdown',
        'description': 'Shuts down the Pi In The Sky Camera hardware',
        'version': "1.0",
        'parameters': ['user']
    }

    assert jobTypes('/shutdown').body == {
        'name': 'shutdown',
        'description': 'Shuts down the Pi In The Sky Camera hardware',
        'version': "1.0",
        'parameters': ['user']
    }

    assert jobTypes('/farts').code == 404
