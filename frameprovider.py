"""
Description
--
Provides various frame sources (camera, video, random pictures)
"""

# System imports
import random
import glob
import os
from typing import Any, Dict, List

# 3rd party imports
import cv2

# Local imports
from threadable import ConsumerProducer


class RandomStoredImageFrameProvider(ConsumerProducer):
    def __init__(self, folder: str, out_channels: Dict[str, List[Any]] = None):
        """
        Description
        --
        - folder - the folder where the .jpg files are
        - out_channels - (see base)
        """

        super().__init__(out_channels=out_channels)
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

        return {ConsumerProducer.channel_main: cv2.imread(random.choice(glob.glob(os.path.join(self._folder, "*.jpg"))))}


class VideoFrameProvider(ConsumerProducer):
    def __init__(self, source: Any = 0, out_channels: Dict[str, List[Any]] = None):
        """
        Description
        --
        Initializes the instance.

        Parameters
        --
        - source - 0 for camera, otherwise str path to video.
        - out_channels - (see base)
        """

        super().__init__(out_channels=out_channels)
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
            return {ConsumerProducer.channel_main: frame}

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
