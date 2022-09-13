from pinthesky import api, set_stream_logger
from pinthesky.globals import request, response
from pinthesky.resource import inject, iot, cameras, groups, subscriptions, videos, tags, stats


for res in [cameras, inject, iot, groups, videos, subscriptions, tags, stats]:
    set_stream_logger(res.__name__)


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
