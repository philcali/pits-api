from botocore.exceptions import ClientError
from collections import namedtuple
from uuid import uuid4
from pinthesky.globals import app_context
from unittest.mock import MagicMock
import pytest


Subscriber = namedtuple(
    'Subscriber',
    field_names=['arn', 'attributes'],
    defaults=[None, {}])


@pytest.fixture(scope="module")
def created_subs():
    sns = MagicMock()
    sns.Topic = MagicMock()
    topic = MagicMock()
    sns.Topic.return_value = topic
    created_subs = {}

    def create(Protocol, Endpoint, ReturnSubscriptionArn, Attributes=None):
        if Endpoint == 'nobody@gmail.com':
            id = str(uuid4())
        else:
            id = 'fail'
        arn = ':'.join(["arn:test", id])
        created_subs[id] = Subscriber(arn=arn)
        return created_subs[id]

    topic.subscribe = MagicMock()
    topic.subscribe.side_effect = create

    sns.Subscription = MagicMock()

    def get(arn):
        id = arn.split(':')[-1]
        if id == 'fail':
            raise ClientError({
                'Error': {
                    'Code': 'NotAuthorized'
                }
            }, "sns:GetSubscriptionAttrinutes")
        elif id in created_subs:
            subscriber = MagicMock()
            return subscriber
        else:
            raise ClientError({
                'Error': {
                    'Code': 'NotFound'
                }
            }, "sns:GetSubscriptionAttributes")

    sns.Subscription.side_effect = get

    app_context.inject('sns', sns, force=True)
    app_context.inject('topic_arn', "arn:test", force=True)
    return created_subs


def test_subscription_workflow(subscriptions, created_subs):
    # List, confirm empty
    assert subscriptions().body == {
        'items': [],
        'nextToken': None
    }

    # Subscribe
    created_sub = subscriptions(method="POST", body={
        'protocol': 'EMAIL',
        'endpoint': 'nobody@gmail.com'
    })

    assert created_sub.code == 200
    sub = created_sub.body
    assert sub['id'] in created_subs

    # Get
    assert subscriptions(f'/{sub["id"]}').code == 200
    assert subscriptions(f'/{sub["id"]}').body == sub

    # Not Found
    assert subscriptions('/farts').code == 404

    # update
    assert subscriptions(f'/{sub["id"]}', method="PUT", body=sub).code == 200
    assert subscriptions('/farts', method="PUT", body=sub).code == 404

    # delete
    assert subscriptions(f'/{sub["id"]}', method="DELETE").code == 200

    # induced failure
    created_failure = subscriptions(method="POST", body={
        'protocol': 'EMAIL',
        'endpoint': 'failure@gmail.com'
    })

    failure = created_failure.body
    assert subscriptions(f'/{failure["id"]}').code == 500
