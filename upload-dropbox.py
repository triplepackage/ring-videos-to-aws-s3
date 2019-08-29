import dropbox
import os
from ring_doorbell import Ring
import urllib.request
from datetime import timedelta, date
import pytz
import configparser
import boto3
from botocore.exceptions import ClientError


class BotoUploader:
    s3_client = boto3.client('s3')
    bucket_name = None

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def uploadfile(self, path, filename):
        try:
            self.s3_client.upload_file(filename, self.bucket_name, path)
        except ClientError as e:
            print(e)


class DropboxUploader:
    dbx = None
    root_directory = None

    def __init__(self, token, root_dir):
        self.dbx = dropbox.Dropbox(token)
        self.root_directory = root_dir

    def file_exists(self, filepath):
        try:
            filepath = os.path.join(self.root_directory, filepath)
            self.dbx.files_get_metadata(filepath)
            return True
        except:
            return False

    def uploadfile(self, filepath, file_destination):
        f = open(filepath)
        file_size = os.path.getsize(filepath)
        file_destination = os.path.join(self.root_directory, file_destination)

        CHUNK_SIZE = 4 * 1024 * 1024

        if file_size <= CHUNK_SIZE:
            print (self.dbx.files_upload(f.read(), file_destination))
        else:
            with open(filepath, 'rb') as f:
                contents = f.read(CHUNK_SIZE)
                upload_session_start_result = self.dbx.files_upload_session_start(contents)
                cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
                                                           offset=f.tell())
                commit = dropbox.files.CommitInfo(path=file_destination)

                while f.tell() < file_size:
                    if ((file_size - f.tell()) <= CHUNK_SIZE):
                        print (self.dbx.files_upload_session_finish(f.read(CHUNK_SIZE), cursor, commit))
                    else:
                        self.dbx.files_upload_session_append(f.read(CHUNK_SIZE), cursor.session_id, cursor.offset)

                        cursor.offset = f.tell()
        f.close()


class RingVideo:
    url = None
    filepath = None
    filename = None

    def __init__(self, url, filepath, filename):
        self.url = url
        self.filepath = filepath
        self.filename = filename


class RingCamera:
    ring = None
    camera = None
    history_limit = 200
    videos = []

    def __init__(self, username, password, history_limit):
        self.ring = Ring(username, password)
        self.history_limit = history_limit
        if self.ring.is_connected:
            self.camera = self.ring.stickup_cams[0]

    def get_motion_videos_by_date(self, datetodownload, timezone):
        video_history = self.camera.history(limit=self.history_limit)
        for history in video_history:
            if history['kind'] == 'motion' and history['created_at'].astimezone(timezone).date() == datetodownload:
                filepath = history['created_at'].astimezone(timezone).strftime("%Y/%m/%d")
                filename = history['created_at'].astimezone(timezone).strftime("%Y-%m-%d-%H-%M-%S") + ".mp4"

                path = os.path.join(filepath, filename)

                self.videos.append(RingVideo(self.camera.recording_url(history['id']), path, filename))

        return self.videos


def main():
    config = configparser.ConfigParser()
    config.read('dropbox.ini')
    dropboxuploader = DropboxUploader(config['DEFAULT']['token'], "/Ring-Videos/")

    config.read('ring-api.ini')
    myring = RingCamera(config['DEFAULT']['username'], config['DEFAULT']['password'], 200)

    botouploader = BotoUploader("ring-camera-videos")

    yesterday = date.today() - timedelta(days=1)
    est = pytz.timezone('US/Eastern')

    videos = myring.get_motion_videos_by_date(yesterday, est)

    for video in videos:
        urllib.request.urlretrieve(video.url, video.filename)
        botouploader.uploadfile(video.filepath, video.filename)

        if not dropboxuploader.file_exists(video.filepath):
            dropboxuploader.uploadfile(video.filename, video.filepath)

        os.remove(video.filename)
        print(video.filepath)


main()
