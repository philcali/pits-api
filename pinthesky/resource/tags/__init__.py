import json
from pinthesky.conversion import hashed_video
from pinthesky.database import QueryParams, Repository, Tags, TagsToVideos, VideosToTags
from pinthesky.exception import ConflictException, NotFoundException
from pinthesky.globals import app_context, request, response
from pinthesky.resource import api
from pinthesky.resource.helpers import create_query_params

app_context.inject('tag_data', Tags())
app_context.inject('tag_video_data', TagsToVideos())
app_context.inject('video_tag_data', VideosToTags())


@api.route('/tags')
def list_tags(tag_data):
    results = tag_data.items(
        request.account_id(),
        params=create_query_params(request=request)
    )
    return {
        'items': results.items,
        'nextToken': results.next_token
    }


@api.route('/tags/:tag_name')
def get_tag(tag_data, tag_name):
    item = tag_data.get(request.account_id(), item_id=tag_name)
    if item is None:
        response.status_code = 404
        return {
            'message': f'Tag with name {tag_name} does not exists.'
        }
    return item


@api.route('/tags', methods=['POST'])
def create_tag(tag_data):
    tag = json.loads(request.body)
    if "name" not in tag:
        response.status_code = 401
        return {
            'message': 'Tag name is a required field'
        }
    try:
        return tag_data.create(request.account_id(), item=tag)
    except ConflictException as e:
        response.status_code = 409
        return {
            'message': str(e)
        }


@api.route('/tags/:tag_name', methods=['PUT'])
def update_tag(tag_data, tag_name):
    tag = json.loads(request.body)
    tag['name'] = tag_name
    try:
        return tag_data.update(request.account_id(), item=tag)
    except NotFoundException as e:
        response.status_code = 404
        return {
            'message': str(e)
        }


@api.route('/tags/:tag_name', methods=['DELETE'])
def delete_tag(tag_data, tag_video_data, video_tag_data, tag_name):
    updates = [{
        'repository': tag_data,
        'delete': True,
        'item': {
            'name': tag_name
        }
    }]
    truncated = True
    next_token = None
    while truncated:
        page = tag_video_data.items(
            request.account_id(),
            tag_name,
            params=QueryParams(next_token=next_token)
        )
        for item in page.items:
            updates.append({
                'repository': tag_video_data,
                'parent_ids': [tag_name],
                'delete': True,
                'item': {
                    'id': item['id']
                }
            })
            updates.append({
                'repository': video_tag_data,
                'parent_ids': [item['id']],
                'delete': True,
                'item': {
                    'id': tag_name
                }
            })
        next_token = page.next_token
        truncated = next_token is not None
    Repository.batch_write(request.account_id(), updates=updates)


@api.route('/tags/:tag_name/videos', methods=['GET'])
def list_tagged_videos(tag_video_data, first_index, tag_name):
    page = tag_video_data.items_index(
        request.account_id(),
        tag_name,
        index_name=first_index,
        params=create_query_params(
            request=request,
            sort_order='descending'
        )
    )
    return {
        'items': page.items,
        'nextToken': page.next_token
    }


@api.route('/tags/:tag_name/videos', methods=['POST'])
def tag_videos(tag_video_data, video_tag_data, tag_name):
    input = json.loads(request.body)
    if 'videos' not in input:
        response.status_code = 401
        return {'message': 'Tagging requires videos.'}
    updates = []
    for index, video in enumerate(input['videos']):
        for field in ['thingName', 'motionVideo', 'duration', 'expiresIn']:
            if field not in video:
                response.status_code = 401
                return {'message': f'Item {index} is missing required fields'}
        gen_id = hashed_video(video['motionVideo'], video['thingName'])
        create_time = int(video['motionVideo'].split('.')[0])
        updates.append({
            'repository': tag_video_data,
            'parent_ids': [tag_name],
            'item': {
                'id': gen_id,
                'motionVideo': video['motionVideo'],
                'thingName': video['thingName'],
                'duration': video['duration'],
                'expiresIn': video['expiresIn'],
                'createTime': create_time,
                'GS1-PK': tag_video_data.make_hash_key(
                    request.account_id(),
                    tag_name
                )
            }
        })
        updates.append({
            'repository': video_tag_data,
            'parent_ids': [gen_id],
            'item': {
                'id': tag_name,
                'expiresIn': video['expiresIn']
            }
        })
    Repository.batch_write(request.account_id(), updates=updates)


@api.route('/tags/:tag_name/videos/:video_id', methods=['DELETE'])
def untag_videos(tag_video_data, video_tag_data, tag_name, video_id):
    updates = []
    updates.append({
        'repository': tag_video_data,
        'parent_ids': [tag_name],
        'delete': True,
        'item': {
            'id': video_id
        }
    })
    updates.append({
        'repository': video_tag_data,
        'parent_ids': [video_id],
        'delete': True,
        'item': {
            'id': tag_name
        }
    })
    Repository.batch_write(request.account_id(), updates=updates)
