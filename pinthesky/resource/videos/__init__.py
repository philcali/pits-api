import json
from pinthesky import api
from pinthesky.conversion import sort_filters_for
from pinthesky.database import MAX_ITEMS, MotionVideos, QueryParams
from pinthesky.globals import app_context, request, response
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
    sort_filters = sort_filters_for('createTime', start_time, end_time)
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


@api.route('/videos/:motion_video/cameras/:camera_name')
def get_motion_video(motion_videos_data, motion_video, camera_name):
    item = motion_videos_data.get(
        request.account_id(),
        camera_name,
        item_id=motion_video)
    if item is None:
        response.status_code = 404
        return {'message': f'Motion video {motion_video} does not exist'}
    return item


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
