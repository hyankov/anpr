"""
Description
--
License plate scanner on the go.

Author
--
Hristo Yankov
"""

# 3rd party imports
import pytesseract

# Local imports
import frameprovider as fp
import platefinder as pf
import platelookup as pl
import ocr as ocr
from interface import Cv2UserInterface


""" Entry point """
if __name__ == '__main__':
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

    # TODO: Make the interface main .Start() point
    interface = Cv2UserInterface(limit=24)

    frame_provider = fp.VideoFrameProvider(
        'images\\VID_20200205_080142.mp4',
        [
            interface,
            pf.PlateFinder(
                [
                    # TODO: Separate channels
                    interface,
                    ocr.Ocr(
                        [
                            pl.PlateLookup(
                                [
                                    # TODO: Separate channel
                                    # interface
                                ]
                            )
                        ],
                        10
                    )
                ],
                10
            )
        ]
    ).start()

    # Start blocking
    interface.start_ui()

    # Stop the services
    frame_provider.stop()
