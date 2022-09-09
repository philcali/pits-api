import hashlib
import json
from pinthesky.conversion import sort_filters_for
from pinthesky.database import MAX_ITEMS, QueryParams, Repository, Tags, TagsToVideos, VideosToTags
from pinthesky.exception import ConflictException, NotFoundException
from pinthesky.globals import app_context, request, response
from pinthesky.resource import api

app_context.inject('tag_data', Tags())
app_context.inject('tag_video_data', TagsToVideos())
app_context.inject('video_tag_data', VideosToTags())


@api.route('/tags')
def list_tags(tag_data):
    limit = int(request.queryparams.get('limit', MAX_ITEMS))
    limit = min(MAX_ITEMS, max(1, limit))
    next_token = request.queryparams.get('nextToken', None)
    results = tag_data.items(
        request.account_id(),
        params=QueryParams(
            limit=limit,
            next_token=next_token
        )
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
        'item': {
            'name': tag_name,
            'delete': True
        }
    }]
    params = QueryParams()
    while True:
        page = tag_video_data.items(
            request.account_id(),
            tag_name,
            params=params
        )
        for item in page.items:
            updates.append({
                'repository': tag_video_data,
                'parent_ids': [tag_name],
                'item': {
                    'id': item['id'],
                    'delete': True
                }
            })
            updates.append({
                'repository': video_tag_data,
                'parent_ids': [item['id']],
                'item': {
                    'id': tag_name,
                    'delete': True
                }
            })
        params = QueryParams(next_token=page.next_token)
        if params.next_token is None:
            break
    Repository.batch_write(request.account_id(), updates=updates)


@api.route('/tags/:tag_name/videos', methods=['GET'])
def list_tagged_videos(tag_video_data, first_index, tag_name):
    limit = int(request.queryparams.get('limit', MAX_ITEMS))
    limit = min(MAX_ITEMS, max(1, limit))
    next_token = request.queryparams.get('nextToken', None)
    start_time = request.queryparams.get('startTime', None)
    end_time = request.queryparams.get('endTime', None)
    sort_asc = request.queryparams.get('order', 'descending') == 'ascending'
    sort_filters = sort_filters_for('createTime', start_time, end_time)
    page = tag_video_data.items_index(
        request.account_id(),
        tag_name,
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


@api.route('/tags/:tag_name/videos', methods=['POST'])
def tag_videos(tag_video_data, video_tag_data, tag_name):
    input = json.loads(request.body)
    if 'videos' not in input:
        response.status_code = 401
        return {'message': 'Tagging requires videos.'}
    updates = []
    for index, video in enumerate(input['videos']):
        for field in ['thingName', 'motionVideo', 'duration']:
            if field not in video:
                response.status_code = 401
                return {'message': f'Item {index} is missing required fields'}
        hash = hashlib.sha256(f'{video["motionVideo"]}:{video["thingName"]}')
        gen_id = hash.hexdigest()
        create_time = int(video['motionVideo'].split('.')[0])
        updates.append({
            'repository': tag_video_data,
            'parent_ids': [tag_name],
            'item': {
                'id': gen_id,
                'motionVideo': video['motionVideo'],
                'thingName': video['thingName'],
                'duration': video['duration'],
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
                'id': tag_name
            }
        })
    Repository.batch_write(request.account_id(), updates=updates)


@api.route('/tags/:tag_name/videos/:video_id', methods=['DELETE'])
def untag_videos(tag_video_data, video_tag_data, tag_name, video_id):
    updates = []
    updates.append({
        'repository': tag_video_data,
        'parent_ids': [tag_name],
        'item': {
            'id': video_id,
            'delete': True
        }
    })
    updates.append({
        'repository': video_tag_data,
        'parent_ids': [video_id],
        'item': {
            'id': tag_name,
            'delete': True
        }
    })
    Repository.batch_write(request.account_id(), updates=updates)
