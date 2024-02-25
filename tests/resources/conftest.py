from botocore.exceptions import ClientError
from datetime import datetime
from pinthesky.globals import app_context
from unittest.mock import MagicMock
from resources import Resources
import pytest


@pytest.fixture(scope="module")
def tags(table):
    assert table.name == 'Pits'
    from pinthesky.resource import tags

    return Resources(tags)


@pytest.fixture(scope="module")
def videos(table):
    assert table.name == 'Pits'
    from pinthesky.resource import videos

    return Resources(videos)


@pytest.fixture(scope="module")
def subscriptions(table):
    assert table.name == 'Pits'
    from pinthesky.resource import subscriptions

    return Resources(subscriptions)


@pytest.fixture(scope="module")
def groups(table):
    assert table.name == 'Pits'
    from pinthesky.resource import groups

    return Resources(groups)


@pytest.fixture(scope="module")
def stats(table):
    assert table.name == 'Pits'
    from pinthesky.resource import stats

    return Resources(stats)


@pytest.fixture(scope="module")
def jobs(table):
    assert table.name == 'Pits'
    from pinthesky.resource import jobs

    return Resources(jobs)


@pytest.fixture(scope="module")
def iot():
    from pinthesky.resource import iot

    return Resources(iot)


@pytest.fixture(scope="module")
def cameras(table):
    assert table.name == 'Pits'
    from pinthesky.resource import cameras

    iot = MagicMock()
    iot_data = MagicMock()

    def side_effect(Bucket, Key):
        if Key == 'images/PitsCamera1/thumbnail_latest.jpg':
            return {
                'ContentType': 'text/plain',
                'ContentLength': 100,
                'LastModified': datetime.now()
            }
        else:
            raise ClientError({
                'Error': {
                    'Code': '404'
                }
            }, 'head_object')
    s3 = MagicMock()
    s3.head_object = MagicMock()
    s3.head_object.side_effect = side_effect
    app_context.inject('iot', iot, force=True)
    app_context.inject('iot_data', iot_data, force=True)
    app_context.inject('s3', s3, force=True)
    return Resources(cameras)
