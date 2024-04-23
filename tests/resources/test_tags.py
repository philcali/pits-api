from math import floor
from time import time
from pinthesky.conversion import hashed_video
from ophis.globals import app_context


def test_tag_crud_workflow(tags, videos):
    motion_videos = app_context.resolve('GLOBAL')['motion_videos_data']

    # List, confirm empty
    assert tags.request().body == {
        'items': [],
        'nextToken': None
    }

    assert tags('/Favorites').code == 404

    created_tag = tags(method="POST", body={
        'name': 'Favorites'
    })

    assert tags(method="POST", body={}).code == 401

    assert created_tag.code == 200
    tag = created_tag.body

    assert tags(method="POST", body=tag).code == 409
    assert tags("/Favorites").body == tag
    assert tag in tags().body['items']

    assert tags('/Favorites', method="PUT", body=tag).code == 200
    assert tags('/Farts', method="PUT", body=tag).code == 404

    title = f'{floor(time())}.motion.mp4'
    # Create some videos
    video = motion_videos.create(
        tags.account_id(),
        'PitsCamera1',
        item={
            'GS1-PK': motion_videos.make_hash_key(tags.account_id()),
            'motionVideo': title,
            'thingName': 'PitsCamera1',
            'duration': 30,
            'expiresIn': floor(time())
        })

    assert videos().body['items'][0] == video
    assert tags('/Favorites/videos', method="POST", body={}).code == 401
    assert tags('/Favorites/videos', method="POST", body={
        'videos': [video]
    }).code == 204
    assert videos(
        f'/{video["motionVideo"]}/cameras/PitsCamera1'
    ).body == video
    assert videos(
        f'/{video["motionVideo"]}/cameras/PitsCamera1',
        method="DELETE").code == 204
    assert videos(
        f'/{video["motionVideo"]}/cameras/PitsCamera1'
    ).code == 404

    video = motion_videos.create(
        tags.account_id(),
        'PitsCamera1',
        item={
            'GS1-PK': motion_videos.make_hash_key(tags.account_id()),
            'motionVideo': title,
            'thingName': 'PitsCamera1',
            'duration': 30,
            'expiresIn': floor(time()),
            'createTime': video['createTime'],
            'updateTime': video['updateTime'],
        })
    assert tags('/Favorites/videos', method="POST", body={
        'videos': [video]
    }).code == 204

    video['id'] = hashed_video(video['motionVideo'], 'PitsCamera1')
    assert tags('/Favorites/videos').body['items'][0] == video
    assert tags(f'/Favorites/videos/{title}', method="DELETE").code == 204

    assert tags('/Favorites/videos', method="POST", body={
        'videos': [video]
    }).code == 204

    assert tags('/Favorites', method="DELETE").code == 204
