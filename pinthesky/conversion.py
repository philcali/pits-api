import hashlib
import dateutil.parser
from math import floor

from pinthesky.database import SortFilter


def isoformat_to_timestamp(date_string):
    return floor(dateutil.parser.isoparse(date_string).timestamp())


def timestamp_to_motion(timestamp):
    return f'{timestamp}.motion.mp4'


def identity_func(t):
    return t


def hashed_video(motion_video, camera_name):
    hash = hashlib.sha256()
    hash.update(bytes(f'{motion_video}:{camera_name}', encoding='utf8'))
    return hash.hexdigest()


def sort_filters_for(field, start_time, end_time, format=None):
    sort_filters = []
    if format is None:
        format = identity_func
    if start_time is not None and end_time is not None:
        start_timestamp = isoformat_to_timestamp(start_time)
        end_timestamp = isoformat_to_timestamp(end_time)
        sort_filters.append(SortFilter(
            name=field,
            method='between',
            values=[format(start_timestamp), format(end_timestamp)]
        ))
    elif start_time is not None:
        sort_filters.append(SortFilter(
            name=field,
            method='gt',
            values=[format(isoformat_to_timestamp(start_time))]
        ))
    elif end_time is not None:
        sort_filters.append(SortFilter(
            name=field,
            method='lt',
            values=[format(isoformat_to_timestamp(end_time))]
        ))
    return sort_filters
