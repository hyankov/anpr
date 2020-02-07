"""
Description
--
Finds objects on the frame.
"""

# System imports
from typing import Any, Tuple

# 3rd party imports
import cv2
from numpy import ndarray

# Local imports
from threadable import ConsumerProducer


class ObjectFinder(ConsumerProducer):
    channel_crop = 'crop'
    channel_highlight = 'highlight'

    def __init__(self, cascade_file: str, out_channels=None, limit=0) -> None:
        """
        Description
        --
        Initializes the instance.

        Parameters
        --
        - cascade_file - the path to the cascade file to use. It dictates what
        objects are detected.
        - out_channels - (see base)
        - limit - (see base)
        """

        super().__init__(out_channels=out_channels, limit=limit)

        if not cascade_file:
            raise ValueError("cascade_file is required")

        # Load the classifier
        self._watch_cascade = cv2.CascadeClassifier(cascade_file)

        self.min_object_size = (125, 40)
        self.max_object_size = (125 * 3, 40 * 3)
        self.y_crop_ratio = 0.25

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
        cropped_image = original_image[int(orig_y * self.y_crop_ratio): orig_y - int(orig_y * self.y_crop_ratio), 0: orig_x]

        watches = self._watch_cascade.detectMultiScale(
            cropped_image,
            1.05,
            3,
            minSize=self.min_object_size,
            maxSize=self.max_object_size)

        cropped = None
        crop_rectangle = None

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
            crop_rectangle = ((int(x), int(y)), (int(x + w), int(y + h)))

        return (cropped, crop_rectangle)

    def _consume(self, item: Any) -> Any:
        """
        Description
        --
        Consumes the image frame.

        Parameters
        --
        - item - image frame (ndarray)

        Returns
        --
        Tuple: (Object crop (if any), the original image with rectangle now).
        """

        if item is not None:
            return self._get_object_crop(item)

    def _produce(self, item: Any) -> Any:
        """
        Description
        --
        Produces an output, based on the consumed input.

        Parameters
        --
        - item - Tuple: (Object crop, the original image with rectangle now).

        Returns
        --
        The result of processing the item. Will be passed
        to the subscribers.
        """

        if item is not None:
            object_crop, crop_rectangle = item

            return {
                # Main channel - highlighted image
                self.channel_highlight: crop_rectangle,

                # Crop channel - the biggest object on the image
                self.channel_crop: object_crop
            }
