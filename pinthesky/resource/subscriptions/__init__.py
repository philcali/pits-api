from pinthesky.database import Subscriptions
from pinthesky.globals import app_context, request
from pinthesky.resource import api

app_context.inject('subscription_data', Subscriptions())


@api.route('/subscriptions/default')
def get_subscription(subscription_data):
    return request.authorizer()
