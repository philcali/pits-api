import json
from datetime import datetime
from math import floor
from pinthesky import api
from pinthesky.database import MAX_ITEMS, MotionVideos, QueryParams, SortFilter
from pinthesky.globals import app_context, request
from pinthesky.s3 import generate_presigned_url


app_context.inject('motion_videos_data', MotionVideos())


@api.route("/videos")
def list_motion_videos(motion_videos_data, first_index):
    limit = int(request.queryparams.get('limit', MAX_ITEMS))
    limit = min(MAX_ITEMS, max(1, limit))
    next_token = request.queryparams.get('nextToken', None)
    start_time = request.queryparams.get('startTime', None)
    end_time = request.queryparams.get('endTime', None)
    sort_asc = request.queryparams.get('order', 'descending') == 'ascending'
    sort_filters = []
    if start_time is not None and end_time is not None:
        start_timestamp = datetime.fromisoformat(start_time).timestamp()
        end_timestamp = datetime.fromisoformat(end_time).timestamp()
        sort_filters.append(SortFilter(
            name='createTime',
            method='between',
            values=[floor(start_timestamp), floor(end_timestamp)]
        ))
    elif start_time is not None:
        start_timestamp = datetime.fromisoformat(start_time).timestamp()
        sort_filters.append(SortFilter(
            name='createTime',
            method='lt',
            values=[floor(start_timestamp)]
        ))
    elif end_time is not None:
        end_timestamp = datetime.fromisoformat(end_time).timestamp()
        sort_filters.append(SortFilter(
            name='createTime',
            method='gt',
            values=[floor(end_timestamp)]
        ))
    page = motion_videos_data.items_index(
        request.account_id(),
        index_name=first_index,
        params=QueryParams(
            sort_ascending=sort_asc,
            limit=limit,
            next_token=next_token,
            sort_filters=sort_filters))
    return {
        'items': page.items,
        'nextToken': page.next_token
    }


@api.route('/videos/:motion_video/cameras/:camera_name', methods=["PUT"])
def put_motion_video(motion_videos_data, motion_video, camera_name):
    metadata = json.loads(request.body)
    metadata['motionVideo'] = motion_video
    metadata['thingName'] = camera_name
    return motion_videos_data.update(
        request.account_id(),
        camera_name,
        item=metadata)


@api.route('/videos/:motion_video/cameras/:camera_name', methods=["DELETE"])
def delete_motion_video(motion_videos_data, motion_video, camera_name):
    motion_videos_data.delete(
        request.account_id(),
        camera_name,
        item_id=motion_video)


@api.route('/videos/:motion_video/cameras/:camera_name/url')
def get_motion_video_url(
        s3,
        bucket_name,
        video_prefix,
        motion_video,
        camera_name):
    s3Key = f'{video_prefix}/{camera_name}/{motion_video}'
    return generate_presigned_url(s3, bucket_name, s3Key)
