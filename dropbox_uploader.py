import dropbox
import os


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

    def upload_file(self, filepath, file_destination):
        f = open(filepath)
        file_size = os.path.getsize(filepath)
        file_destination = os.path.join(self.root_directory, file_destination)

        CHUNK_SIZE = 4 * 1024 * 1024

        if file_size <= CHUNK_SIZE:
            print(self.dbx.files_upload(f.read(), file_destination))
        else:
            with open(filepath, 'rb') as f:
                contents = f.read(CHUNK_SIZE)
                upload_session_start_result = self.dbx.files_upload_session_start(contents)
                cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
                                                           offset=f.tell())
                commit = dropbox.files.CommitInfo(path=file_destination)

                while f.tell() < file_size:
                    if (file_size - f.tell()) <= CHUNK_SIZE:
                        print(self.dbx.files_upload_session_finish(f.read(CHUNK_SIZE), cursor, commit))
                    else:
                        self.dbx.files_upload_session_append(f.read(CHUNK_SIZE), cursor.session_id, cursor.offset)

                        cursor.offset = f.tell()
        f.close()