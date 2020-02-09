"""
Description
--
User interface module.
"""

# System imports
from typing import Any

# 3rd party imports
import cv2

# Local imports
from threadable import WorkerPipe


class Cv2UserInterface(WorkerPipe):
    """
    Simple cv2-based user interface.
    """

    window_name = "Main"

    def _consume(self, item: Any) -> Any:
        """
        Description
        --
        Renders the consumed frames.

        Parameters
        --
        - item - the frame to render.

        """

        if item is None:
            # Bad/dead feed
            self.stop()
        else:
            cv2.imshow(self.window_name, item)

            if cv2.waitKey(1) == 27:
                # ESC pressed, exit
                self.stop()

    def _on_starting(self) -> None:
        """
        Description
        --
        Called before the main loop.
        """

        # We sleep with waitKey()
        self._main_loop_sleep_s = 0

        # Prepare the visual window
        cv2.namedWindow(self.window_name)  # cv2.WND_PROP_FULLSCREEN)
        # cv2.resizeWindow(self.window_name, 320, 240)
        # cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    def _on_stopped(self) -> None:
        """
        Description
        --
        Called after the main loop.
        """

        # Main UI loop ended, destroy all windows
        cv2.destroyAllWindows()
