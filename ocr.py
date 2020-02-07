"""
Description
--
OCR service.
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
        OCR-ed string.
        """

        if item is None:
            return

        # cv2.imshow("plate_crop", item)
        # cv2.waitKey(1)

        image_crop = cv2.resize(item, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

        # Pre-processing
        image_crop = cv2.medianBlur(image_crop, 5)
        image_crop = cv2.adaptiveThreshold(
            cv2.cvtColor(image_crop, cv2.COLOR_RGB2GRAY),
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            8)

        # cv2.imshow("ocr", plate_crop)

        # Get the text out of the pre-processed plate image
        text = pytesseract.image_to_string(
            Image.fromarray(image_crop),
            config='--psm 7 -l eng -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')

        # TODO: Confidence

        print(text)
        return text
