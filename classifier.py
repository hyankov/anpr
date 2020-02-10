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
from threadable import WorkerPipe


class ObjectFinder(WorkerPipe):
    channel_found_object_crop = 'channel_found_object_crop'
    channel_found_object_coords = 'channel_found_object_coords'

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

        # Tuned for license plates, by default
        self.min_object_size = (125, 40)
        self.max_object_size = (125 * 3, 40 * 3)
        self.y_crop_ratio = 0.25
        self.scale = 1.10       # 1.05 to 1.4
        self.min_neighbors = 4  # 3 to 6

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
        # See https://stackoverflow.com/a/20805153/253266
        # See https://dev.to/petercour/car-number-plate-detection-with-python-4n7g

        orig_y, orig_x, _ = original_image.shape

        # Only process the center of the image
        # TODO: Calibration (choose what part of the screen to process)
        y_padding = int(orig_y * self.y_crop_ratio)
        cropped_image = original_image[y_padding: orig_y - y_padding, 0: orig_x]

        watches = self._watch_cascade.detectMultiScale(
            cropped_image,
            self.scale,
            self.min_neighbors,
            minSize=self.min_object_size,
            maxSize=self.max_object_size)

        if watches is not None and len(watches) > 0:
            # Widest rectangle first
            watch = sorted(watches, key=lambda watch: watch[2])[0]

            (x, y, w, h) = watch

            # Magic
            """
            x -= w * 0.14
            w += w * 0.28
            y -= h * 0.15
            h += h * 0.3
            """

            # Crop the object
            cropped = self._crop_image(cropped_image, (int(x), int(y), int(w), int(h))).copy()

            # Get the object highlight (rectangle around it)
            crop_rectangle = (
                (
                    int(x),
                    int(y) + y_padding
                ),
                (
                    int((x + w) * self.scale),
                    int((y + y_padding + h) * self.scale)
                )
            )

            # Found
            return (cropped, crop_rectangle)

        # Not found
        return None

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
                    # Coords channel - detected object coordinates on frame
                    self.channel_found_object_coords: crop_rectangle,

                    # Crop channel - cropped image of the detected object
                    self.channel_found_object_crop: object_crop
                }
