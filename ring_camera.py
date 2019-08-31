from ring_doorbell import Ring
import os


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
    cameras = None
    history_limit = 200
    videos = []

    def __init__(self, username, password, history_limit):
        self.ring = Ring(username, password)
        self.history_limit = history_limit
        if self.ring.is_connected:
            if self.ring.stickup_cams is not None and len(self.ring.stickup_cams) > 0:
                self.cameras = self.ring.stickup_cams
            else:
                raise Exception("Unable to connect to find any devices")
        else:
            raise Exception("Unable to connect to the Ring API")

    def get_motion_videos_by_date(self, date_to_download, timezone):
        for camera in self.cameras:
            video_history = camera.history(limit=self.history_limit)
            video_history = [x for x in video_history if (x['created_at'].astimezone(timezone).date() ==
                                                          date_to_download and x['kind'] == 'motion')]
            for history in video_history:
                directory = history['created_at'].astimezone(timezone).strftime("%Y/%m/%d")
                filename = camera.name + \
                    history['created_at'].astimezone(timezone).strftime("-%Y-%m-%d-%H-%M-%S") + ".mp4"

                path = os.path.join(directory, filename)

                self.videos.append(RingVideo(camera.recording_url(history['id']), path, filename))

        return self.videos
