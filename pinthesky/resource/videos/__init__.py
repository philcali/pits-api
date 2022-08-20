from datetime import datetime
from math import floor
from pinthesky import api
from pinthesky.database import MAX_ITEMS, MotionVideos, QueryParams, SortFilter
from pinthesky.globals import app_context, request


app_context.inject('motion_videos', MotionVideos())


@api.route("/videos")
def list_motion_videos(motion_videos, first_index):
    limit = int(request.queryparams.get('limit', MAX_ITEMS))
    limit = min(MAX_ITEMS, max(1, limit))
    next_token = request.queryparams.get('nextToken', None)
    start_time = request.queryparams.get('startTime', None)
    end_time = request.queryparams.get('endTime', None)
    filters = []
    if start_time is not None and end_time is not None:
        start_timestamp = datetime.fromisoformat(start_time).timestamp()
        end_timestamp = datetime.fromisoformat(end_time).timestamp()
        filters.append(SortFilter(
            name='createTime',
            method='between',
            values=[floor(start_timestamp), floor(end_timestamp)]
        ))
    elif start_time is not None:
        start_timestamp = datetime.fromisoformat(start_time).timestamp()
        filters.append(SortFilter(
            name='createTime',
            method='lt',
            values=[floor(start_timestamp)]
        ))
    elif end_time is not None:
        end_timestamp = datetime.fromisoformat(end_time).timestamp()
        filters.append(SortFilter(
            name='createTime',
            method='gt',
            values=[floor(end_timestamp)]
        ))
    page = motion_videos.items_index(
        request.account_id,
        index_name=first_index,
        params=QueryParams(
            limit=limit,
            next_token=next_token,
            filters=filters))
    return {
        'items': page.items,
        'nextToken': page.next_token
    }
