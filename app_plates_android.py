"""
Description
--
Setting up the workers for a license plate recognition
and lookup.
"""

# Local imports
from workers import feed as fp
from workers import classifier as of
from workers import interface as ui
from logger import log


""" Entry point """
if __name__ == '__main__':
    # Load logging configuration
    log.config()

    # Create workers
    interface = ui.Cv2UserInterface(jobs_limit=30)
    frame_feed = fp.FrameFeed(fp.IPCameraFrameProvider("http://127.0.0.1:8080"), jobs_limit=60)
    object_finder = of.ObjectFinder('classifiers\\mn_license_plates.xml', jobs_limit=1)

    # Video feed -> Object Finder | UI
    frame_feed\
        .link_to(object_finder, frame_feed.channel_raw)\
        .link_to(interface, frame_feed.channel_processed)

    # Object Finder -> Video feed | OCR
    object_finder\
        .link_to(frame_feed, object_finder.channel_object_rectangle)\
        .y_crop_ratio = 0.25            # Crop upper and lower 1/4th of the images
    object_finder.scale = 1.4           # Fast processing
    object_finder.min_neighbors = 5     # High confidence

    # Start the workers
    object_finder.start()
    frame_feed.start()
    interface.start(True)

    # Interface stopped, stop the workers ...
    frame_feed.stop()
    object_finder.stop()
