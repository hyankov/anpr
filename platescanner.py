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
import feed as fp
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
    interface = ui.Cv2UserInterface(jobs_limit=30)
    video_feed = fp.VideoFeed('images\\VID_20200205_080142.mp4', jobs_limit=128)
    object_finder = of.ObjectFinder('classifiers\\generic_license_plates.xml', jobs_limit=1)
    plate_lookup = pl.PlateLookup(jobs_limit=5)
    ocr_service = ocr.Ocr(jobs_limit=5)

    # Video feed -> Object Finder | UI
    video_feed\
        .link_to(object_finder, video_feed.channel_raw)\
        .link_to(interface, video_feed.channel_processed)

    # Object Finder -> Video feed | OCR
    object_finder\
        .link_to(video_feed, object_finder.channel_found_object_coords)\
        .link_to(ocr_service, object_finder.channel_found_object_crop)\
        # .main_loop_sleep_s = 0.1

    # OCR -> Plate Lookup
    ocr_service.link_to(plate_lookup, ocr_service.channel_text)

    # Plate lookup -> Video feed
    # plate_lookup.link_to(video_feed, plate_lookup.channel_plate_info)

    # Start the pipes
    plate_lookup.start()
    ocr_service.start()
    object_finder.start()
    video_feed.start()
    interface.start(True)

    # Interface stopped, stop the pipes ...
    video_feed.stop()
    object_finder.stop()
    ocr_service.stop()
    plate_lookup.stop()
