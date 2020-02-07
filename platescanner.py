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
from threadable import ConsumerProducer as cp


""" Entry point """
if __name__ == '__main__':
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

    # TODO: Make the interface main .Start() point
    interface = Cv2UserInterface()

    # TODO: Fluent syntax for adding subscribers
    frame_provider = fp.VideoFrameProvider('images\\VID_20200205_080142.mp4')

    frame_provider._out_channels = {
            cp.channel_main: [
                interface,
                pf.PlateFinder(
                    {
                        pf.PlateFinder.channel_highlight: [
                            frame_provider
                        ],
                        pf.PlateFinder.channel_crop: [
                            ocr.Ocr(
                                {
                                    cp.channel_main: [
                                        pl.PlateLookup(
                                            {
                                                cp.channel_main: [
                                                    #frame_provider
                                                ]
                                            })
                                    ]
                                })
                        ]
                    }, 5)
            ]
        }

    frame_provider.start()

    # Start blocking
    interface.start_ui()

    # Stop the services
    frame_provider.stop()
