"""
Description
--
License plate OCR.
"""

# System imports
import cv2
import pytesseract
from PIL import Image
from typing import Any

# Local imports
from threadable import ConsumerProducer


class Ocr(ConsumerProducer):
    def _consume(self, item: Any) -> Any:
        """
        Description
        --
        Consumes a work item.

        Parameters
        --
        - item - image frame (ndarray)

        Returns
        --
        License plate string.
        """

        if item is None:
            return

        # cv2.imshow("plate_crop", plate_crop)

        plate_crop = cv2.resize(item, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

        # Pre-processing
        plate_crop = cv2.medianBlur(plate_crop, 5)
        plate_crop = cv2.adaptiveThreshold(
            cv2.cvtColor(plate_crop, cv2.COLOR_RGB2GRAY),
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            8)

        # cv2.imshow("ocr", plate_crop)

        # Get the text out of the pre-processed plate image
        plate_number = pytesseract.image_to_string(
            Image.fromarray(plate_crop),
            config='--psm 7 -l eng -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')

        # TODO: Confidence

        print(plate_number)
        return plate_number
