"""
Description
--
Finds plate numbers on the frame.
"""

# System imports
from typing import List, Any, Tuple

# 3rd party imports
import cv2
from numpy import ndarray

# Local imports
from threadable import ConsumerProducer


class PlateFinder(ConsumerProducer):
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

    def _get_plate_crops(self, original_image: ndarray, resize_h=720, en_scale=1.04) -> Tuple[List[ndarray], ndarray]:
        watches = self._watch_cascade.detectMultiScale(
            original_image,
            en_scale,
            2,
            minSize=(36, 9))

        sorted(watches, key=lambda watch: watch[2])

        cropped_images = []  # type List[ndarray]
        for (x, y, w, h) in watches:
            # Magic
            x -= w * 0.14
            w += w * 0.28
            y -= h * 0.15
            h += h * 0.3

            # Crop the plate
            cropped = self._crop_image(original_image, (int(x), int(y), int(w), int(h))).copy()
            cropped_images.append(cropped)

            # Highlight the plate
            cv2.rectangle(original_image, (int(x), int(y)), (int(x + w), int(y + h)), (255, 0, 255), 3)

        return (cropped_images, original_image)

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
        Tuple: (Plate crops (if any), the original image with rectangles now).
        """

        if item is not None:
            return self._get_plate_crops(item, item.shape[0])

    def _produce(self, item: Any) -> Any:
        """
        Description
        --
        Produces an output, based on the consumed input.

        Parameters
        --
        - item - Tuple: (Plate crops (if any), the original image with rectangles now).

        Returns
        --
        The result of processing the item. Will be passed
        to the subscribers.
        """

        if item is not None:
            plate_crops, original_image = item

            if plate_crops:
                # The first (biggest) plate crop
                return plate_crops[0]

    def start(self) -> Any:
        """
        Description
        --
        Overrides.
        """

        # Load the classifier
        self._watch_cascade = cv2.CascadeClassifier('cascade.xml')

        return super().start()
