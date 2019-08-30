import boto3
from botocore.exceptions import ClientError


class BotoUploader:
    s3_client = boto3.client('s3')
    bucket_name = None

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def upload_file(self, path, filename):
        try:
            self.s3_client.upload_file(filename, self.bucket_name, path)
        except ClientError as e:
            print(e)