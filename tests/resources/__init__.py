from pinthesky import api
from collections import namedtuple
from string import Template
import json

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
