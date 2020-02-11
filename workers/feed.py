"""
Description
--
Provides various frame sources (camera, video, random pictures)
"""

# System imports
from typing import Any, Dict, Tuple
import os
import urllib3
import ssl

# 3rd party imports
import cv2
import numpy as np

# Local imports
from .worker import Worker


class FrameProvider:
    def start(self) -> None:
        pass

    def get(self) -> Tuple[bool, Any]:
        return (False, None)

    def stop(self) -> None:
        pass


class IPCameraFrameProvider(FrameProvider):
    def __init__(self, url: str):
        if not url:
            raise ValueError("url is required")

        self._url = url

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    def get(self) -> Tuple[bool, Any]:
        try:
            img_resp = urllib3.urlopen(self._url)
            img_np = np.array(bytearray(img_resp.read()), dtype=np.uint8)

            return (True, cv2.imdecode(img_np, -1))
        except Exception:
            return (False, None)


class CameraFrameProvider(FrameProvider):
    def __init__(self, camera_index: int = 0) -> None:
        """
        Description
        --
        Initializes the instance.

        Parameters
        --
        - source - The camera index.
        """

        self._source = camera_index
        self._stream = None

    def start(self):
        # Get a handle on the stream
        self._stream = cv2.VideoCapture(self._source)

    def get(self) -> Tuple[bool, Any]:
        return self._stream.read()

    def stop(self):
        # Release the stream
        self._stream.release()


class VideoFrameProvider(CameraFrameProvider):
    def __init__(self, video_file_path: str) -> None:
        """
        Description
        --
        Initializes the instance.

        Parameters
        --
        - video_file_path - The path to the video file.
        """

        if not video_file_path:
            raise ValueError("video_file_path is required")

        if not os.path.isfile(video_file_path):
            raise ValueError("File not found {}".format(video_file_path))

        self._source = video_file_path
        self._stream = None


class FrameFeed(Worker):
    channel_raw = "channel_raw"
    channel_processed = "channel_processed"

    def __init__(self, frame_provider: FrameProvider = CameraFrameProvider(), jobs_limit=0) -> None:
        """
        Description
        --
        Initializes the instance.

        Parameters
        --
        - source - 0 for camera, otherwise str path to video.
        - jobs_limit - (see base)
        """

        super().__init__(jobs_limit=jobs_limit)

        # Rectangle properties
        self.rectangle_border_color = (255, 0, 255)
        self.rectangle_border_width = 2

        # For how many frames should a rectangle be cached
        self.cache_highlight_for = 0  # 0 for no caching

        # We don't want the feed source to wait for a job
        # in the queue.
        self._wait_for_job_s = 0

        self._frame_provider = frame_provider
        self._stream = None
        self._cached_highlight = None
        self._cached_highlights_count = 0

    def _process_input_job(self, input_job: Any) -> Dict[str, Any]:
        """
        Description
        --
        Produce a frame. If there is an input job, it's an overlay
        to put on the frame.

        Parameters
        --
        - input_job - information to overlay, if any.

        Returns
        --
        Raw image (without an overlay) and an image with an overlay.
        """

        grabbed, frame = self._frame_provider.get()

        if grabbed:
            # If caching is enabled ...
            if self.cache_highlight_for:
                if input_job:
                    # Pulled a fresh highlight, reset cache
                    self._cached_highlight = input_job
                    self._cached_highlights_count = 0
                else:
                    # No highlight, get from cache
                    if self._cached_highlight is not None:
                        input_job = self._cached_highlight
                        self._cached_highlights_count += 1

                        if self._cached_highlights_count == self.cache_highlight_for:
                            # Expire the cache
                            self._cached_highlight = None
                            self._cached_highlights_count = 0

            overlay_frame = frame

            if input_job:
                # Overlay a rectangle
                a, b = input_job
                overlay_frame = frame.copy()
                cv2.rectangle(overlay_frame, a, b, self.rectangle_border_color, self.rectangle_border_width)

            return {
                self.channel_raw: frame,
                self.channel_processed: overlay_frame
            }
        else:
            # End of the stream
            self.stop()

    def _on_starting(self) -> None:
        """
        Description
        --
        Called before the main loop.
        """

        self._frame_provider.start()

    def _on_stopped(self) -> None:
        """
        Description
        --
        Called after the main loop.
        """

        self._frame_provider.stop()
