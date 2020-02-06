"""
Description
--
Provides various frame sources (camera, video, random pictures)
"""

# System imports
import random
import glob
import os
from typing import Any, List

# 3rd party imports
import cv2

# Local imports
from threadable import ConsumerProducer


class RandomStoredImageFrameProvider(ConsumerProducer):
    def __init__(self, folder: str, subscribers: List[Any] = []):
        """
        Description
        --
        - folder - the folder where the .jpg files are
        - subscribers - (see base)
        """

        super().__init__(subscribers=subscribers)
        self._folder = folder

    def _get_next(self) -> Any:
        # Optimization
        pass

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

        return cv2.imread(random.choice(glob.glob(os.path.join(self._folder, "*.jpg"))))


class VideoFrameProvider(ConsumerProducer):
    def __init__(self, source: Any = 0, subscribers: List[Any] = []):
        """
        Description
        --
        Initializes the instance.

        Parameters
        --
        - source - 0 for camera, otherwise str path to video.
        - subscribers - (see base)
        """

        super().__init__(subscribers=subscribers)
        self._source = source
        self._stream = None

    def _get_next(self) -> Any:
        # Optimization
        pass

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
        The next frame.
        """

        grabbed, frame = self._stream.read()

        if grabbed:
            return frame

    def _service_stopped(self) -> None:
        """
        Description
        --
        Called when the service is stopped.
        """

        # Release the stream
        self._stream.release()

    def start(self) -> Any:
        """
        Description
        --
        Overrides.
        Starts capture.
        """

        # Get a handle on the stream
        self._stream = cv2.VideoCapture(self._source)

        return super().start()
