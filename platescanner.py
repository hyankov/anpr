"""
Description
--
Setting up the workers for a license plate recognition
and lookup.
"""

# Local imports
import feed as fp
import classifier as of
import platelookup as pl
import ocr as ocr
import interface as ui
import log


""" Entry point """
if __name__ == '__main__':
    # Load logging configuration
    log.config()

    # Create workers
    interface = ui.Cv2UserInterface(False, jobs_limit=30)
    video_feed = fp.VideoFeed(0, jobs_limit=60)  # 'videos\\mn_video1.mp4'
    object_finder = of.ObjectFinder('classifiers\\mn_license_plates.xml', jobs_limit=1)
    plate_lookup = pl.PlateLookup(jobs_limit=5)
    ocr_service = ocr.Ocr(jobs_limit=5)

    # Video feed -> Object Finder | UI
    video_feed\
        .link_to(object_finder, video_feed.channel_raw)\
        .link_to(interface, video_feed.channel_processed)

    # Object Finder -> Video feed | OCR
    object_finder\
        .link_to(video_feed, object_finder.channel_object_rectangle)\
        .link_to(ocr_service, object_finder.channel_object_crop)\
        # .y_crop_ratio = 0.16  # Crop upper and lower 1/6th of the images
    object_finder.scale = 1.05
    object_finder.min_neighbors = 5

    # OCR -> Plate Lookup
    ocr_service.link_to(plate_lookup, ocr_service.channel_text)

    # Plate lookup -> Video feed
    # plate_lookup.link_to(video_feed, plate_lookup.channel_plate_info)

    # Start the workers
    plate_lookup.start()
    ocr_service.start()
    object_finder.start()
    video_feed.start()
    interface.start(True)

    # Interface stopped, stop the workers ...
    video_feed.stop()
    object_finder.stop()
    ocr_service.stop()
    plate_lookup.stop()
