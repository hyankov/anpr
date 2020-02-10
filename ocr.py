"""
Description
--
OCR service.
"""

# System imports
import cv2
import pytesseract
from PIL import Image
from typing import Any, Dict

# Local imports
from worker import Worker


class Ocr(Worker):
    channel_text = "channel_text"

    def _process_input_job(self, input_job: Any) -> Dict[str, Any]:
        """
        Description
        --
        OCRs an image.

        Parameters
        --
        - input_job - An image which to OCR.

        Returns
        --
        The text on the image.
        """

        if input_job is None:
            return

        # cv2.imshow("plate_crop", item)
        # cv2.waitKey(1)

        image_crop = cv2.resize(input_job, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

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

        if text:
            # TODO: Confidence
            self._logger.info(text)

            return {self.channel_text: text}
