"""
Description
--
Provides various frame sources (camera, video, random pictures)
"""

# System imports
import random
import glob
import os
from typing import Any

# 3rd party imports
import cv2

# Local imports
from threadable import WorkerPipe


class RandomStoredImageFrameProvider(WorkerPipe):
    channel_highlighted = "highlighted"

    def __init__(self, folder: str, limit=0):
        """
        Description
        --
        - folder - the folder where the .jpg files are.
        - limit - (see base)
        """

        super().__init__(limit=limit)

        self._folder = folder
        self._is_polling_queue = True
        self._main_loop_sleep = 1

    def _produce(self, item: Any) -> Any:
        """
        Description
        --
        Produces frame output.

        Parameters
        --
        - item - ignored.

        Returns
        --
        The next photo.
        """

        next_image = cv2.imread(random.choice(glob.glob(os.path.join(self._folder, "*.jpg"))))

        if item:
            # overlay the highlighted object
            a, b = item
            cv2.rectangle(next_image, a, b, (0, 0, 255), 3)

            return {self.channel_highlighted: next_image}
        else:
            return {self.channel_main: next_image}


class VideoFrameProvider(WorkerPipe):
    channel_highlighted = "highlighted"

    def __init__(self, source: Any = 0, limit=0):
        """
        Description
        --
        Initializes the instance.

        Parameters
        --
        - source - 0 for camera, otherwise str path to video.
        - limit - (see base)
        """

        super().__init__(limit=limit)

        self._source = source
        self._stream = None
        self._is_polling_queue = True
        # self._main_loop_sleep = 0.5

    def _produce(self, item: Any) -> Any:
        """
        Description
        --
        Produces frame output.

        Parameters
        --
        - item - object highlight, if any.

        Returns
        --
        The next frame.
        """

        grabbed, frame = self._stream.read()

        if grabbed:
            if item:
                # overlay the highlighted object
                a, b = item
                cv2.rectangle(frame, a, b, (0, 0, 255), 3)

                return {self.channel_highlighted: frame}
            else:
                return {self.channel_main: frame}
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
