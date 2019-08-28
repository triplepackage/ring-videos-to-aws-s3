import dropbox
import os
import configparser
from ring_doorbell import Ring
import urllib.request
from datetime import datetime, timedelta, date
import pytz
import configparser

config = configparser.ConfigParser()
config.read('dropbox.ini')

token = config['DEFAULT']['token']

config.read('ring-api.ini')

username = config['DEFAULT']['username']
password = config['DEFAULT']['password']

myring = Ring(username, password)

class DropboxUploader:
	dbx = None
	root_directory = None

	def __init__(self, token, root_dir):
		self.dbx = dropbox.Dropbox(token)
		self.root_directory = root_dir

	def dropbox_file_exists(self, filepath):
		try:
			filepath = os.path.join(self.root_directory, filepath)
			self.dbx.files_get_metadata(filepath)
			return True
		except:
			return False

	def uploadfile(self, filepath, filedestination):
		f = open(filepath)
		file_size = os.path.getsize(filepath)
		filedestination = os.path.join(self.root_directory, filedestination)

		CHUNK_SIZE = 4 * 1024 * 1024

		if file_size <= CHUNK_SIZE:
			print (self.dbx.files_upload(f.read(), filedestination))
		else:
			with open(filepath, 'rb') as f:
				contents = f.read(CHUNK_SIZE)
				upload_session_start_result = self.dbx.files_upload_session_start(contents)
				cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id, offset=f.tell())
				commit = dropbox.files.CommitInfo(path=filedestination)

				while f.tell() < file_size:
					if ((file_size - f.tell()) <= CHUNK_SIZE):
						print (self.dbx.files_upload_session_finish(f.read(CHUNK_SIZE), cursor, commit))
					else:
						self.dbx.files_upload_session_append(f.read(CHUNK_SIZE), cursor.session_id, cursor.offset)

						cursor.offset = f.tell()

		f.close()

def download_ring_videos(camera, datetodownload, timezone, dropboxuploader):
	video_history = camera.history(limit = 200)

	for history in video_history:
		url = camera.recording_url(history['id'])

		if history['kind'] == 'motion' and history['created_at'].astimezone(timezone).date() == datetodownload:
			filepath = history['created_at'].astimezone(timezone).strftime("%Y/%m/%d")
			filename = history['created_at'].astimezone(timezone).strftime("%Y-%m-%d-%H-%M-%S") + ".mp4"

			path = os.path.join(filepath, filename)
			download_video_and_upload(url, filename, path, dropboxuploader)

def download_video_and_upload(url, filename, destination, dropboxuploader):
	if dropboxuploader.dropbox_file_exists(destination) == False:
		urllib.request.urlretrieve(url, filename)
		dropboxuploader.uploadfile(filename, destination)
		os.remove(filename)

yesterday = date.today() - timedelta(days=1)
est = pytz.timezone('US/Eastern')

if myring.is_connected:
	camera = myring.stickup_cams[0]
	dropboxuploader = DropboxUploader(token, "/Ring-Videos/")

	download_ring_videos(camera, yesterday, est, dropboxuploader)
