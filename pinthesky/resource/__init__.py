from pinthesky import api, set_stream_logger
from pinthesky.globals import request, response
from pinthesky.resource import inject, iot, cameras, configuration, groups


for res in [cameras, configuration, inject, iot, groups]:
    set_stream_logger(res.__name__)


@api.filter()
def cors():
    if request.method() == 'OPTIONS':
        response.headers = {
            'access-control-allow-origin': '*',
            'access-control-allow-methods': 'GET, POST, PUT, DELETE',
            'access-control-allow-headers': 'Content-Type, Content-Length, Authorization'
        }
        response.break_continuation()
