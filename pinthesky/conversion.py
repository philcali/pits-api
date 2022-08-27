import dateutil.parser
from math import floor


def isoformat_to_timestamp(date_string):
    return floor(dateutil.parser.isoparse(date_string).timestamp())
