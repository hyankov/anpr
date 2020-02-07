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
from threadable import ConsumerProducer


class RandomStoredImageFrameProvider(ConsumerProducer):
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

        return {ConsumerProducer.channel_main: cv2.imread(random.choice(glob.glob(os.path.join(self._folder, "*.jpg"))))}


class VideoFrameProvider(ConsumerProducer):
    channel_raw = "raw"
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
                # overlay the highlight (there's slight delay)
                a, b = item
                cv2.rectangle(frame, a, b, (0, 0, 255), 3)

                return {self.channel_highlighted: frame}
            else:
                return {self.channel_raw: frame}

    def _service_stopped(self) -> None:
        """
        Description
        --
        Called when the service is stopped.
        """

        super()._service_stopped()

        # Release the stream
        self._stream.release()

    def _service_started(self) -> None:
        """
        Description
        --
        Called when the service is started.
        """

        # Get a handle on the stream
        self._stream = cv2.VideoCapture(self._source)
