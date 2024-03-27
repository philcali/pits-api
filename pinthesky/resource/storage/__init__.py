import boto3

from ophis.globals import app_context
from pinthesky import api


app_context.inject('s3', boto3.client('s3'))


@api.route('/storage/info')
def get_storage_info(bucket_name, video_prefix, image_prefix, device_video_prefix):

    return {
        'bucketName': bucket_name,
        'videoPrefix': video_prefix,
        'imagePrefix': image_prefix,
        'deviceVideoPrefix': device_video_prefix,
    }
