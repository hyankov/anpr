"""
Description
--
A configuration which is setup to detect and read
Minnesota license plates.
"""

# Local imports
from workers import feed as fp
from workers import classifier as of
from workers import platelookup as pl
from workers import ocr as ocr
from workers import interface as ui
from logger import log


""" Entry point """
if __name__ == '__main__':
    # Load logging configuration
    log.config()

    # Create workers
    interface = ui.Cv2UserInterface(jobs_limit=30)
    # frame_feed = fp.FrameFeed(fp.VideoFrameProvider('videos\\mn_video1.mp4'), jobs_limit=60)
    frame_feed = fp.FrameFeed(fp.CameraFrameProvider(), jobs_limit=60)
    object_finder = of.ObjectFinder('classifiers\\mn_license_plates.xml', jobs_limit=1)
    plate_lookup = pl.PlateLookup(jobs_limit=5)
    ocr_service = ocr.Ocr(jobs_limit=5)

    # Video feed -> Object Finder | UI
    frame_feed\
        .link_to(object_finder, frame_feed.channel_raw)\
        .link_to(interface, frame_feed.channel_processed)

    # Object Finder -> Video feed | OCR
    object_finder\
        .link_to(frame_feed, object_finder.channel_object_rectangle)\
        .link_to(ocr_service, object_finder.channel_object_crop)\
        .y_crop_ratio = 0.25            # Crop upper and lower 1/4th of the images
    object_finder.scale = 1.4           # Fast processing
    object_finder.min_neighbors = 5     # High confidence

    # OCR -> Plate Lookup
    ocr_service.link_to(plate_lookup, ocr_service.channel_text)

    # Plate lookup -> Frame feed
    # plate_lookup.link_to(frame_feed, plate_lookup.channel_plate_info)

    # Start the workers
    plate_lookup.start()
    ocr_service.start()
    object_finder.start()
    frame_feed.start()
    interface.start(True)

    # Interface stopped, stop the workers ...
    frame_feed.stop()
    object_finder.stop()
    ocr_service.stop()
    plate_lookup.stop()
