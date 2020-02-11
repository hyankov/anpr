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
from .worker import Worker


class Ocr(Worker):
    channel_text = "channel_text"

    def _pre_process_image(self, img):
        pre_processed_image = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

        pre_processed_image = cv2.medianBlur(pre_processed_image, 5)
        pre_processed_image = cv2.adaptiveThreshold(
            cv2.cvtColor(pre_processed_image, cv2.COLOR_RGB2GRAY),
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            8)

        return pre_processed_image

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

        # TODO: The OCR is of very bad quality right now. Improve.

        # Pre-processing
        image_crop = self._pre_process_image(input_job)

        # cv2.imshow("ocr", image_crop)
        # cv2.waitKey(1)

        # Get the text out of the pre-processed plate image
        text = pytesseract.image_to_string(
            Image.fromarray(image_crop),
            config='--psm 7 -l eng -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')

        if text:
            # TODO: Confidence
            self._logger.info(text)

            return {self.channel_text: text}
