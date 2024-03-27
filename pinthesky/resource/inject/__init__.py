import boto3
import os
from ophis.globals import app_context

TABLE_NAME = os.getenv('TABLE_NAME', 'Pits')

ddb = boto3.resource('dynamodb')
app_context.inject('dynamodb', ddb)
app_context.inject('table', ddb.Table(TABLE_NAME))
app_context.inject('first_index', os.getenv('INDEX_NAME_1', 'GS1'))
app_context.inject('bucket_name', os.getenv('BUCKET_NAME', 'NOT_FOUND'))
app_context.inject('image_prefix', os.getenv('IMAGE_PREFIX', 'images'))
app_context.inject('video_prefix', os.getenv('VIDEO_PREFIX', 'videos'))
app_context.inject('device_video_prefix', os.getenv('DEFAULT_VIDEO_PREFIX', 'devices'))
app_context.inject('topic_arn', os.getenv('TOPIC_ARN'))
