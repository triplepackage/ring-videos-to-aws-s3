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
dbx = dropbox.Dropbox(token)

est = pytz.timezone('US/Eastern')

config.read('ring-api.ini')

username = config['DEFAULT']['username']
password = config['DEFAULT']['password']

myring = Ring(username, password)

yesterday = date.today() - timedelta(days=1)

def uploadfile(filepath, filedestination):
	f = open(filepath)
	file_size = os.path.getsize(filepath)

	CHUNK_SIZE = 4 * 1024 * 1024

	if file_size <= CHUNK_SIZE:
	    print (dbx.files_upload(f.read(), filedestination))
	else:
		with open(filepath, 'rb') as f:
			contents = f.read(CHUNK_SIZE)
			upload_session_start_result = dbx.files_upload_session_start(contents)
			cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id, offset=f.tell())
			commit = dropbox.files.CommitInfo(path=filedestination)

			while f.tell() < file_size:
				if ((file_size - f.tell()) <= CHUNK_SIZE):
					print (dbx.files_upload_session_finish(f.read(CHUNK_SIZE), cursor, commit))
				else:
					dbx.files_upload_session_append(f.read(CHUNK_SIZE), cursor.session_id, cursor.offset)

					cursor.offset = f.tell()

		f.close()

if myring.is_connected:
    camera = myring.stickup_cams[0]
    video_history = camera.history(limit = 200)
    for history in video_history:
        url = camera.recording_url(history['id'])

        if history['created_at'].astimezone(est).date() == yesterday:
	        filepath = history['created_at'].astimezone(est).strftime("%Y/%m/%d")
	        filename = history['created_at'].astimezone(est).strftime("%Y-%m-%d-%H-%M-%S") + ".mp4"

	        urllib.request.urlretrieve(url, filename)

	        path = os.path.join(filepath, filename)

	        uploadfile(filename, "/" + path)

	        os.remove(filename)
