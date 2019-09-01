#!/usr/bin/python

import os
import urllib.request
from datetime import timedelta, date
import pytz
import configparser
from math import floor
from boto_uploader import BotoUploader
from dropbox_uploader import DropboxUploader
from ring_camera import RingCamera


def floored_percentage(val, digits):
    val *= 10 ** (digits + 2)
    return '{1:.{0}f}%'.format(digits, floor(val) / 10 ** digits)


def process_videos():
    config = configparser.ConfigParser()
    config.read('config.ini')
    dropbox_uploader = DropboxUploader(config['Dropbox']['token'], config['Dropbox']['root_folder'])

    ring_camera = RingCamera(config['Ring']['username'], config['Ring']['password'], 200)

    boto_uploader = BotoUploader("ring-camera-videos")

    yesterday = date.today() - timedelta(days=1)
    est = pytz.timezone(config['Ring']['timezone'])

    print("Retrieving videos for " + yesterday.strftime("%m/%d/%Y") + "...")
    videos = ring_camera.get_motion_videos_by_date(yesterday, est)

    for video in videos:
        urllib.request.urlretrieve(video.url, video.filename)
        boto_uploader.upload_file(video.filepath, video.filename)

        if not dropbox_uploader.file_exists(video.filepath):
            dropbox_uploader.upload_file(video.filename, video.filepath)

        os.remove(video.filename)
        progress = videos.index(video) / len(videos)
        print(floored_percentage(progress, 2) + " processed")


if __name__ == '__main__':
    process_videos()
    print("All videos processed")
