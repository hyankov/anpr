"""
Description
--
Finds objects on the frame.
"""

# System imports
from typing import Any, Dict, Tuple

# 3rd party imports
import cv2
from numpy import ndarray

# Local imports
from worker import Worker


class ObjectFinder(Worker):
    channel_object_crop = 'channel_object_crop'
    channel_object_rectangle = 'channel_object_rectangle'

    def __init__(self, cascade_file: str, jobs_limit=0) -> None:
        """
        Description
        --
        Initializes the instance.

        Parameters
        --
        - cascade_file - the path to the cascade file to use. It dictates what
        objects are detected.
        - jobs_limit - (see base)
        """

        super().__init__(jobs_limit=jobs_limit)

        if not cascade_file:
            raise ValueError("cascade_file is required")

        self.min_object_size = None  # type: Tuple(int, int)
        self.max_object_size = None  # type: Tuple(int, int)
        self.scale = 1.25       # 1.05 to 1.4
        self.min_neighbors = 5  # 3 to 6

        # TODO: User-specified
        # A crop ratio of 1/4 (0.25) means the image is split in 4 and the
        # upper and bottom 1/4 parts are cropped out. 0 for no-cropping
        self.y_crop_ratio = 0

        # Load the classifier
        self._watch_cascade = cv2.CascadeClassifier(cascade_file)

    def _crop_image(self, image, rect):
        x, y, w, h = self._compute_safe_region(image.shape, rect)

        return image[y:y + h, x:x + w]

    def _compute_safe_region(self, shape, bounding_rect):
        top = bounding_rect[1]  # y
        bottom = bounding_rect[1] + bounding_rect[3]  # y +  h
        left = bounding_rect[0]  # x
        right = bounding_rect[0] + bounding_rect[2]  # x +  w
        min_top = 0
        max_bottom = shape[0]
        min_left = 0
        max_right = shape[1]

        if top < min_top:
            top = min_top
        if left < min_left:
            left = min_left
        if bottom > max_bottom:
            bottom = max_bottom
        if right > max_right:
            right = max_right

        return [left, top, right - left, bottom - top]

    def _get_object_crop(self, original_image: ndarray) -> Tuple[ndarray, ndarray]:
        orig_y, orig_x, _ = original_image.shape

        # Crop the image to particular area we're interested in
        y_padding = int(orig_y * self.y_crop_ratio)
        cropped_image = original_image[y_padding: orig_y - y_padding, 0: orig_x]

        # See https://stackoverflow.com/a/20805153/253266
        detections = self._watch_cascade.detectMultiScale(
            cropped_image,
            self.scale,
            self.min_neighbors,
            minSize=self.min_object_size,
            maxSize=self.max_object_size)

        if detections is None or len(detections) == 0:
            # No detection
            return None

        # Widest rectangle first
        detection = sorted(detections, key=lambda d: d[2])[0]

        (x, y, w, h) = detection

        # Crop the object
        cropped = self._crop_image(cropped_image, (int(x), int(y), int(w), int(h))).copy()

        # Get the object highlight (rectangle around it)
        crop_rectangle = (
            (
                int(x),
                int(y) + y_padding
            ),
            (
                int((x + w)),
                int((y + y_padding + h))
            )
        )

        # Found
        return (cropped, crop_rectangle)

    def _process_input_job(self, input_job: Any) -> Dict[str, Any]:
        """
        Description
        --
        Finds object in the image. The input is the image.

        Parameters
        --
        - input_job - image in which to find the object the
        classifier has been trained for.

        Returns
        --
        If found, tuple of cropped image of the object
        and rectangle. Otherwise None.
        """

        if input_job is not None:
            result = self._get_object_crop(input_job)

            if result:
                object_crop, crop_rectangle = result

                return {
                    # Rectangle channel - detected object rectangle X, Y, W, H
                    self.channel_object_rectangle: crop_rectangle,

                    # Crop channel - cropped image of the detected object
                    self.channel_object_crop: object_crop
                }
