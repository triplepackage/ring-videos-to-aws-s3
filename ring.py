from ring_doorbell import Ring
import urllib.request
from datetime import datetime
import pytz
import configparser
import logging
import boto3
from botocore.exceptions import ClientError
import os

est = pytz.timezone('US/Eastern')

config = configparser.ConfigParser()
config.read('ring-api.ini')

username = config['DEFAULT']['username']
password = config['DEFAULT']['password']

myring = Ring(username, password)

s3_client = boto3.client('s3')

if myring.is_connected:
    camera = myring.stickup_cams[0]
    video_history = camera.history(limit = 200)
    for history in video_history:
        url = camera.recording_url(history['id'])
        print(history['created_at'].astimezone(est).strftime("%Y-%m-%d-%H-%M-%S") + ".mp4")
        if history['created_at'].astimezone(est).strftime("%d") == '26':
            filepath = history['created_at'].astimezone(est).strftime("%Y/%m/%d")
            filename = history['created_at'].astimezone(est).strftime("%Y-%m-%d-%H-%M-%S") + ".mp4"

            urllib.request.urlretrieve(url, filename)

            path = os.path.join(filepath, filename)
            print(path)

            try:
                response = s3_client.upload_file(filename, "ring-camera-videos", path)
            except ClientError as e:
                logging.error(e)
