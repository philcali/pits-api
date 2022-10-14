import functools
import json
import boto3
import os
import socket
import subprocess
import sys
from collections import namedtuple
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pinthesky import set_stream_logger
from pinthesky.globals import app_context
from uuid import uuid4


Context = namedtuple('Context', field_names=['invoked_function_arn'])


class RouterRequet(BaseHTTPRequestHandler):
    def __init__(
            self,
            *args,
            router=None,
            function_arn=None,
            auth_local=False,
            **kwargs):
        if router is None:
            from pinthesky.resource import api
            router = api
        self.router = router
        self.auth_local = auth_local
        if function_arn is None:
            function_arn = ':'.join([
                'arn',
                'aws',
                'lambda',
                'us-east-1',
                '012345678912',
                'function',
                'TestFunction'
            ])
        self.function_arn = function_arn
        super().__init__(*args, **kwargs)

    def route_request(self) -> None:
        parts = self.path.split('?', 1)
        path = parts[0]
        rawQueryParameters = ''
        if len(parts) == 2:
            path, rawQueryParameters = parts
        queryStringParameters = {}
        if rawQueryParameters != '':
            for parameter in rawQueryParameters.split("&"):
                key, value = parameter.split('=', 1)
                if key in queryStringParameters:
                    queryStringParameters[key] += f',{value}'
                else:
                    queryStringParameters[key] = value
        event = {
            "version": "2.0",
            "routeKey": "$default",
            "rawPath": path,
            "rawQueryString": rawQueryParameters,
            "queryStrinParameters": queryStringParameters,
            "headers": {k: v for k, v in self.headers.items()},
            "cookies": self.headers.get_all('cookie', []),
            "requestContext": {
                "accountId": "123456789012",
                "apiId": "test-api",
                "authorizer": {
                    "jwt": {
                        "claims": {
                            "username": os.getenv("USER")
                        }
                    }
                },
                "http": {
                    "method": self.command,
                    "path": path,
                    "protocol": self.request_version
                }
            },
            "requestId": str(uuid4()),
            "routeKey": "$default",
            "stage": "$default",
        }
        length = int(self.headers.get("content-length", 0))
        if length > 0:
            event['body'] = self.rfile.read(length)
        resp = self.router(event, Context(
            invoked_function_arn=self.function_arn
        ))
        self.send_response(resp['statusCode'])
        for k, v in resp['headers'].items():
            self.send_header(k, v)
        self.end_headers()
        if resp.get('body', None) is not None:
            self.wfile.write(bytes(resp['body'], 'utf-8'))

    def is_auth(self):
        return "oauth2" in self.path or "logout" in self.path

    def _parse_query(self):
        parts = self.path.split('?', 1)
        raw_query = parts[1]
        params = {}
        for parameter in raw_query.split('&'):
            key, value = parameter.split('=', 1)
            params[key] = value
        return params

    def handle_auth(self):
        params = self._parse_query()
        self.send_response(302)
        ex = 24 * 60 * 60
        resp = f'#id_token={uuid4()}&access_token={uuid4()}&expires_in={ex}'
        self.send_header("Location", params['redirect_uri'] + resp)
        self.end_headers()

    def handle_logout(self):
        params = self._parse_query()
        self.send_response(302)
        self.send_error("Location", params['redirect_uri'])
        self.end_headers()

    def user_info(self):
        resp = {
            'id': os.getenv("USER"),
            'username': os.getenv("USER"),
            'email': f'{os.getenv("USER")}@gmail.com'
        }
        resp_body = json.dumps(resp)
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Access-Control-Allow-Headers', ', '.join([
            'Content-Type',
            'Content-Length',
            'Authorization'
        ]))
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(resp_body))
        self.end_headers()
        self.wfile.write(bytes(resp_body, 'utf-8'))

    def handle_one_request(self) -> None:
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                return
            if not self.raw_requestline:
                self.close_connection = True
                return
            if not self.parse_request():
                return
            if self.auth_local and self.is_auth():
                if "authorize" in self.path:
                    self.handle_auth()
                elif "userInfo" in self.path:
                    self.user_info()
                elif "logout" in self.path:
                    self.handle_logout()
                else:
                    self.send_response(404, "Not Found")
            else:
                self.route_request()
            self.wfile.flush()
        except TimeoutError as e:
            self.log_error("Request timed out: %r", e)
            self.close_connection = True
            return


def _create_local_table(dynamodb):
    table = dynamodb.create_table(
        TableName='Pits',
        KeySchema=[
            {
                'AttributeName': 'PK',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'SK',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'PK',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'SK',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'GS1-PK',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'createTime',
                'AttributeType': 'N'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        },
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'GS1',
                'KeySchema': [
                    {
                        'AttributeName': 'GS1-PK',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'createTime',
                        'KeyType': 'RANGE'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            }
        ]
    )
    table.wait_until_exists()
    app_context.inject('dynamodb', dynamodb, force=True)
    app_context.inject('table', table, force=True)
    yield table
    app_context.remove('dynamodb')
    app_context.remove('table')


def _override_local_dynamodb(args):
    proc_args = [
        "java", "-Djava.library.path=dynamodb/DynamoDBLocal_list",
        "-jar", "dynamodb/DynamoDBLocal.jar",
        "-port", f'{args.dynamodb_port}'
    ]
    if args.dynamodb_memory:
        proc_args.append("-inMemory")
    else:
        proc_args.append("-sharedDb")
        if args.dynamodb_db_path is not None:
            proc_args.append("-dbPath")
            proc_args.append(args.dynamodb_db_path)
    proc = subprocess.Popen(proc_args)
    yield boto3.resource(
        'dynamodb',
        region_name="us-east-1",
        aws_access_key_id="fake",
        aws_secret_access_key="fake",
        endpoint_url=f'http://localhost:{args.dynamodb_port}'
    )
    proc.kill()


def _create_parser():
    import argparse
    parser = argparse.ArgumentParser(
        "pinthesky-local",
        description="runs a local, disconnected copy of the pits-api"
    )
    parser.add_argument(
        "--port",
        type=int,
        default="8080",
        help="sets the port number used for the server (default: 8080)"
    )
    parser.add_argument(
        "--address",
        default=None,
        help="which address to bind"
    )
    parser.add_argument(
        '--auth-local',
        action="store_true",
        help="spins up a local authentication and authorization server"
    )
    parser.add_argument(
        "--dynamodb-local",
        action="store_true",
        help="spins up a local DynamoDB server"
    )
    parser.add_argument(
        "--dynamodb-port",
        default="8000",
        help="the port used for the local DynamoDB server"
    )
    parser.add_argument(
        "--dynamodb-memory",
        action="store_true",
        help="whether or not the database is stored entirely in memory"
    )
    parser.add_argument(
        "--dynamodb-db-path",
        required=False,
        help="where to write the DynamoDB local shared database"
    )
    return parser


def main():
    set_stream_logger('pinthesky')

    parser = _create_parser()
    args = parser.parse_args(sys.argv[1:])
    gen_dynamodb = gen_table = None
    if args.dynamodb_local:
        gen_dynamodb = _override_local_dynamodb(args)
        gen_table = _create_local_table(next(gen_dynamodb))
        next(gen_table)

    def _get_best_family(*address):
        infos = socket.getaddrinfo(
            *address,
            type=socket.SOCK_STREAM,
            flags=socket.AI_PASSIVE,
        )
        family, type, proto, canonname, sockaddr = next(iter(infos))
        return family, sockaddr
    HTTPServer.address_family, addr = _get_best_family(
        args.address,
        args.port
    )
    create_route = functools.partial(
        RouterRequet,
        auth_local=args.auth_local)
    with HTTPServer(addr, create_route) as httpd:
        host, port = httpd.socket.getsockname()[:2]
        url_host = f'[{host}' if ':' in host else host
        print(
            f'Servicing HTTP on {host} port {port}',
            f'(http://{url_host}:{port}/) ...'
        )
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            for gen in [gen_table, gen_dynamodb]:
                if gen_table is not None:
                    try:
                        gen.send(1)
                    except StopIteration:
                        print('Stopping generator')
            print("\nKeyboard interrupt received, exiting.")
            sys.exit(0)


if __name__ == '__main__':
    main()
