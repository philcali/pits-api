import json
from pinthesky.resource import api, response
from pinthesky.resource.jobs import JOB_TYPES

JOB_PARAMETERS = {
    'shutdown': [
        'user'
    ],
    'reboot': [
        'user'
    ],
    'update': [
        'user',
        'version'
    ],
}


def _create_job_type(job_name):
    document = json.loads(JOB_TYPES[job_name])
    return {
        'name': job_name,
        'description': document['_comment'],
        'version': document['version'],
        'parameters': JOB_PARAMETERS[job_name]
    }


@api.route('/jobTypes')
def list_job_types():
    return {
        'items': [_create_job_type(job_name) for job_name in JOB_PARAMETERS.keys()],
        'nextToken': None
    }


@api.route('/jobTypes/:job_name')
def describe_job_type(job_name):
    if job_name not in JOB_PARAMETERS:
        response.status_code = 404
        return {
            'message': f'Job of name {job_name} does not exist.'
        }
    return _create_job_type(job_name)
