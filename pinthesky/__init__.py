import logging
from pinthesky.router import Router


def set_stream_logger(name="pinthesky", level=logging.INFO, fmt_string=None):
    if fmt_string is None:
        fmt_string = "%(asctime)s %(name)s [%(levelname)s] %(message)s"

    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter(fmt_string)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class NullHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        pass


logging.getLogger('pinthesky').addHandler(NullHandler())

api = Router()
