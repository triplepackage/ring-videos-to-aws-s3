import dropbox
import os
import configparser
from ring_doorbell import Ring
import urllib.request
from datetime import datetime, timedelta, date
import pytz
import configparser

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
		video_history = self.camera.history(limit = self.history_limit)
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
	myring = RingCamera(config['DEFAULT']['username'], config['DEFAULT']['password'], 50)

	yesterday = date.today() - timedelta(days=1)
	est = pytz.timezone('US/Eastern')

	for video in myring.get_motion_videos_by_date(yesterday, est):
		if dropboxuploader.file_exists(video.filepath) == False:
			urllib.request.urlretrieve(video.url, video.filename)
			dropboxuploader.uploadfile(video.filename, video.filepath)
			os.remove(video.filename)
			print(video.filepath)

main()
