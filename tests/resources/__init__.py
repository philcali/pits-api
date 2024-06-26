from pinthesky import api
from collections import namedtuple
from string import Template
import json

Response = namedtuple('Response', field_names=['code', 'body', 'headers'])
Context = namedtuple('Context', field_names=['invoked_function_arn'])


class Resources():
    def __init__(self, module) -> None:
        self.module = module
        self.resource_name = module.__name__.split('.')[-1]

    def __call__(self, *args, **kwds):
        return self.request('/'.join(args), **kwds)

    def __read_event(self, path, method="GET", query_params={}, body=None):
        with open('events/resources/request.template.json') as f:
            content = f.read()
            template = Template(content)
            event = json.loads(template.safe_substitute(
                path=path,
                method=method,
                body=json.dumps(json.dumps(body)) if body is not None else '""'
            ))
            event['queryStringParameters'] = query_params
        return event

    def account_id(self):
        event = self.__read_event("/")
        return event['requestContext']['accountId']

    def request(self, name="", method='GET', query_params={}, body=None):
        path = f'/{self.resource_name}{name}'
        event = self.__read_event(
            path=path,
            method=method,
            query_params=query_params,
            body=body,
        )
        res = api(event=event, context=Context(
            invoked_function_arn=':'.join([
                'arn',
                'aws',
                'lambda',
                'us-east-1',
                event['requestContext']['accountId'],
                'function',
                'TestFunction'
            ])
        ))
        return Response(
            code=res['statusCode'],
            body=json.loads(res['body']) if res['body'] is not None else "",
            headers=res['headers']
        )
