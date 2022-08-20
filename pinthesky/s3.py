
def generate_presigned_url(s3, bucket_name, key, expires_in=3600):
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': key},
        ExpiresIn=expires_in)
    return {
        'expiresIn': expires_in,
        'url': url
    }
