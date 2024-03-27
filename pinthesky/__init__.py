import logging
from ophis import set_stream_logger
from ophis.router import Router


logging.getLogger('pinthesky').addHandler(logging.NullHandler())
# TODO: set the level from the ENV
set_stream_logger('pinthesky')

api = Router()
