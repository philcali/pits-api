import json
from pinthesky.database import MAX_ITEMS, QueryParams, Tags, TagsToVideos, VideosToTags
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
def delete_tag(tag_data, tag_name):
    tag_data.delete(request.account_id(), item_id=tag_name)
