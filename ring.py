from ring_doorbell import Ring
import urllib.request
from datetime import datetime, timedelta, date
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

yesterday = date.today() - timedelta(days=1)

if myring.is_connected:
    camera = myring.stickup_cams[0]
    video_history = camera.history(limit = 200)
    for history in video_history:

        if history['created_at'].astimezone(est).date() == yesterday:
            url = camera.recording_url(history['id'])

            filepath = history['created_at'].astimezone(est).strftime("%Y/%m/%d")
            filename = history['created_at'].astimezone(est).strftime("%Y-%m-%d-%H-%M-%S") + ".mp4"

            urllib.request.urlretrieve(url, filename)

            path = os.path.join(filepath, filename)

            try:
                response = s3_client.upload_file(filename, "ring-camera-videos", path)
            except ClientError as e:
                logging.error(e)

            os.remove(filename)
