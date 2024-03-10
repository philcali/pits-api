import json


def test_job_type_operations(jobTypes):
    from pinthesky.resource.jobs import JOB_TYPES

    assert jobTypes().body['items'][0] == {
        'name': 'shutdown',
        'description': 'Shuts down the Pi In The Sky Camera hardware',
        'version': "1.0",
        'parameters': ['user']
    }

    # method to check that all types are properly parameterized
    for job_name, job_json in JOB_TYPES.items():
        parameters = ['user']
        job = json.loads(job_json)
        for step in job['steps']:
            args = step['action']['input'].get('args', [])
            for arg in [a.replace('$', '') for a in args if '$' in a]:
                if arg not in parameters:
                    parameters.append(arg)
        assert jobTypes(f'/{job_name}').body == {
            'name': job_name,
            'description': job['_comment'],
            'version': job['version'],
            'parameters': parameters
        }

    assert jobTypes('/farts').code == 404
