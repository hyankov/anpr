"""
Description
--
Provides various frame sources (camera, video, random pictures)
"""

# System imports
from typing import Any, Dict

# 3rd party imports
import cv2

# Local imports
from threadable import WorkerPipe


class VideoFeed(WorkerPipe):
    channel_raw = "channel_raw"
    channel_processed = "channel_processed"

    def __init__(self, source: Any = 0, jobs_limit=0):
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

        # We don't want the feed source to wait for a job
        # in the queue.
        self._wait_for_job_s = 0

        self._source = source
        self._stream = None
        self._cached_highlight = None
        self._max_cached_highlights_count = 10
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

        grabbed, frame = self._stream.read()

        if grabbed:
            if input_job:
                # Pulled a fresh highlight, reset cache
                self._cached_highlight = input_job
                self._cached_highlights_count = 0
            else:
                # No highlight, get from cache
                if self._cached_highlight is not None:
                    input_job = self._cached_highlight
                    self._cached_highlights_count += 1

                    if self._cached_highlights_count == self._max_cached_highlights_count:
                        # Expire the cache
                        self._cached_highlight = None
                        self._cached_highlights_count = 0

            overlay_frame = frame

            if input_job:
                # Overlay a rectangle
                a, b = input_job
                overlay_frame = frame.copy()
                cv2.rectangle(overlay_frame, a, b, (0, 0, 255), 3)

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

        # Get a handle on the stream
        self._stream = cv2.VideoCapture(self._source)

    def _on_stopped(self) -> None:
        """
        Description
        --
        Called after the main loop.
        """

        # Release the stream
        self._stream.release()
