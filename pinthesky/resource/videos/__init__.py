import json
from ophis.database import QueryParams, Repository
from ophis.globals import app_context, request, response
from pinthesky import api
from pinthesky.conversion import hashed_video
from pinthesky.database import MotionVideos
from pinthesky.resource.helpers import create_query_params
from pinthesky.s3 import generate_presigned_url


app_context.inject('motion_videos_data', MotionVideos())


@api.route("/videos")
def list_motion_videos(motion_videos_data, first_index):
    page = motion_videos_data.items_index(
        request.account_id(),
        index_name=first_index,
        params=create_query_params(
            request=request,
            sort_order='descending'
        ))
    return {
        'items': page.items,
        'nextToken': page.next_token
    }


@api.route('/videos/:motion_video/cameras/:camera_name/tags')
def list_motion_video_tags(video_tag_data, motion_video, camera_name):
    gen_id = hashed_video(motion_video, camera_name)
    page = video_tag_data.items(
        request.account_id(),
        gen_id,
        params=create_query_params(request))
    return {
        'items': page.items,
        'nextToken': page.next_token
    }


@api.route(
    '/videos/:motion_video/cameras/:camera_name/tags/:tag_name',
    methods=['DELETE']
)
def delete_tag_from_video(
        video_tag_data,
        tag_video_data,
        motion_video,
        camera_name,
        tag_name):
    gen_id = hashed_video(motion_video, camera_name)
    updates = [
        {
            'repository': tag_video_data,
            'parent_ids': [tag_name],
            'delete': True,
            'item': {
                'id': gen_id
            }
        },
        {
            'repository': video_tag_data,
            'parent_ids': [gen_id],
            'delete': True,
            'item': {
                'id': tag_name
            }
        }
    ]
    Repository.batch_write(request.account_id(), updates=updates)


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
def delete_motion_video(
        motion_videos_data,
        tag_video_data,
        video_tag_data,
        motion_video,
        camera_name):
    updates = [{
        'repository': motion_videos_data,
        'parent_ids': [camera_name],
        'delete': True,
        'item': {
            'motionVideo': motion_video
        }
    }]
    params = QueryParams()
    while True:
        gen_id = hashed_video(motion_video, camera_name)
        page = video_tag_data.items(
            request.account_id(),
            gen_id,
            params=params
        )
        for item in page.items:
            updates.append({
                'repository': tag_video_data,
                'parent_ids': [item['id']],
                'delete': True,
                'item': {
                    'id': gen_id
                }
            })
            updates.append({
                'repository': video_tag_data,
                'parent_ids': [gen_id],
                'delete': True,
                'item': {
                    'id': item['id']
                }
            })
        params = QueryParams(next_token=page.next_token)
        if params.next_token is None:
            break
    Repository.batch_write(request.account_id(), updates=updates)


@api.route('/videos/:motion_video/cameras/:camera_name/url')
def get_motion_video_url(
        s3,
        bucket_name,
        video_prefix,
        motion_video,
        camera_name):
    s3Key = f'{video_prefix}/{camera_name}/{motion_video}'
    return generate_presigned_url(s3, bucket_name, s3Key)
