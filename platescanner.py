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
from threadable import ConsumerProducer as cp


""" Entry point """
if __name__ == '__main__':
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

    # Create services
    interface = ui.Cv2UserInterface(24)
    frame_provider = fp.VideoFrameProvider(
        #'images'
        'images\\VID_20200205_080142.mp4'
    )
    object_finder = of.ObjectFinder('classifiers\\generic_license_plates.xml', 3)
    ocr_service = ocr.Ocr(5)
    plate_lookup = pl.PlateLookup()

    # Highlighted frames go to ...
    frame_provider.out_channels[fp.VideoFrameProvider.channel_highlighted] = [
        # UI
        interface
    ]

    # Raw frames go to ...
    frame_provider.out_channels[fp.VideoFrameProvider.channel_raw] = [
        # UI and Classifier
        interface, object_finder
    ]

    # Highlighted objects go to ...
    object_finder.out_channels[of.ObjectFinder.channel_highlight] = [
        # Frame provider
        frame_provider
    ]

    # Cropped objects go to ...
    object_finder.out_channels[of.ObjectFinder.channel_crop] = [
        # OCR
        ocr_service
    ]

    # OCRed text goes to ...
    ocr_service.out_channels[cp.channel_main] = [
        # Plate Lookup
        plate_lookup
    ]

    # Plate info goes to ...
    plate_lookup.out_channels[cp.channel_main] = [
        # TODO: frame_provider
    ]

    # Start services
    plate_lookup.start()
    ocr_service.start()
    object_finder.start()
    frame_provider.start()

    # Start blocking
    interface.start(False)

    # Interface stopped, stop the services
    frame_provider.stop()
    object_finder.stop()
    ocr_service.stop()
    plate_lookup.stop()
