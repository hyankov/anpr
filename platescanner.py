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
import classifier as of
import platelookup as pl
import ocr as ocr
import interface as ui
import logger


""" Entry point """
if __name__ == '__main__':
    logger.setup()
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

    # Create worker pipes
    interface = ui.Cv2UserInterface(limit=24)
    frame_provider = fp.VideoFrameProvider('images\\VID_20200205_080142.mp4')
    object_finder = of.ObjectFinder('classifiers\\generic_license_plates.xml', limit=1)
    plate_lookup = pl.PlateLookup(limit=5)
    ocr_service = ocr.Ocr(limit=5)

    # Link the pipes
    frame_provider\
        .link_to(interface)\
        .link_to(object_finder)\
        .link_to(interface, frame_provider.channel_highlighted)

    ocr_service.link_to(plate_lookup)

    object_finder\
        .link_to(frame_provider)\
        .link_to(ocr_service, object_finder.channel_crop)

    # plate_lookup.link_to(frame_provider)

    # Start the pipes
    plate_lookup.start()
    ocr_service.start()
    object_finder.start()
    frame_provider.start()  # TODO: On frame provider stopped
    interface.start(True)

    # Interface stopped, stop the pipes ...
    frame_provider.stop()
    object_finder.stop()
    ocr_service.stop()
    plate_lookup.stop()
