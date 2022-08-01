from contextvars import ContextVar


class _ContextContainer:
    def __init__(self, name, fields) -> None:
        self.__context = {}
        for tag in fields:
            self.__context[tag] = ContextVar(f'{name}_{tag}')

    def __getattr__(self, __name: str) -> any:
        if __name.endswith('__context'):
            return self.__dict__['__context']
        if __name in self.__context:
            return self.__context[__name].get(None)
        raise AttributeError(f'attribute {__name} does not exist')

    def __setattr__(self, __name: str, __value: any) -> None:
        if __name.endswith('__context'):
            self.__dict__['__context'] = __value
        elif __name in self.__context:
            self.__context[__name].set(__value)
        else:
            raise AttributeError(f'attribute {__name} does not exist')


class Request(_ContextContainer):
    def __init__(self) -> None:
        super().__init__("request", [
            "headers",
            "cookies",
            "body",
            "queryparams",
            "event",
            "context"
        ])

    def account_id(self):
        return self.event['requestContext']['accountId']

    def api_id(self):
        return self.event['requestContext']['apiId']

    def remote_addr(self):
        return self.event['requestContext']['http']['sourceIp']

    def method(self):
        return self.event['requestContext']['http']['method']


class Response(_ContextContainer):
    def __init__(self) -> None:
        super().__init__("response", [
            "abort",
            "headers",
            "body",
            "status_code"
        ])

    def is_aborted(self):
        return self.abort is True

    def break_continuation(self):
        self.abort = True
        return self
