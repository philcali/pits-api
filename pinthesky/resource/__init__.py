from pinthesky import api, set_stream_logger
from pinthesky.globals import request, response
from pinthesky.resource import inject, iot, cameras, groups, jobs, jobTypes, subscriptions, videos, tags, stats


for res in [cameras, inject, iot, groups, jobs, jobTypes, videos, subscriptions, tags, stats]:
    set_stream_logger(res.__name__)


@api.filter()
def cors():
    response.headers = {
        'access-control-allow-origin': '*',
        'access-control-allow-methods': 'GET, POST, PUT, DELETE',
        'access-control-allow-headers': ', '.join([
            'Content-Type',
            'Content-Length',
            'Authorization'
        ])
    }
    if request.method() == 'OPTIONS':
        response.break_continuation()
