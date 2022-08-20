import boto3
import os
from pinthesky.globals import app_context

TABLE_NAME = os.getenv('TABLE_NAME')

ddb = boto3.resource('dynamodb')
app_context.inject('table', ddb.Table(TABLE_NAME))
app_context.inject('first_index', os.getenv('INDEX_NAME_1'))
app_context.inject('bucket_name', os.getenv('BUCKET_NAME'))
app_context.inject('image_prefix', os.getenv('IMAGE_PREFIX'))
app_context.inject('video_prefix', os.getenv('VIDEO_PREFIX'))
