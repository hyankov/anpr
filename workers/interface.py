"""
Description
--
User interface module.
"""

# System imports
from typing import Any, Dict

# 3rd party imports
import cv2

# Local imports
from .worker import Worker


class Cv2UserInterface(Worker):
    """
    Simple cv2-based user interface.
    """

    window_name = "Main"

    def __init__(self, full_screen=True, jobs_limit=0):
        """
        Description
        --
        Initializes the instance.

        Parameters
        --
        - full_screen - True for fullscreen, otherwise False.
        - jobs_limit - (see base)
        """

        super().__init__(jobs_limit=jobs_limit)

        self._full_screen = full_screen

        # We sleep with waitKey()
        self.main_loop_sleep_s = 0

    def _process_input_job(self, input_job: Any) -> Dict[str, Any]:
        """
        Description
        --
        Renders the frame.

        Parameters
        --
        - input_job - An image which to render in the UI.
        """

        if input_job is not None:
            cv2.imshow(self.window_name, input_job)

        if cv2.waitKey(1) == 27:
            # ESC pressed, exit
            self.stop()

    def _on_starting(self) -> None:
        """
        Description
        --
        Called before the main loop.
        """

        if self._full_screen:
            # Prepare the visual window
            cv2.namedWindow(self.window_name, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    def _on_stopped(self) -> None:
        """
        Description
        --
        Called after the main loop.
        """

        # Main UI loop ended, destroy all windows
        cv2.destroyAllWindows()
