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
from threadable import ConsumerProducer


class Cv2UserInterface(ConsumerProducer):
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

        if item is not None:
            cv2.imshow(self.window_name, item)

        if cv2.waitKey(1) == 27:
            # ESC pressed, exit
            self.stop()

    def _service_stopped(self) -> None:
        """
        Description
        --
        Called when the service is stopped.
        """

        super()._service_stopped()

        # Main UI loop ended, destroy all windows
        cv2.destroyAllWindows()

    def start(self) -> Any:
        """
        Description
        --
        Overrides.
        """

        # Prepare the visual window
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)  # cv2.WND_PROP_FULLSCREEN)
        # cv2.resizeWindow(self.window_name, 320, 240)
        # cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        return self

    def start_ui(self) -> None:
        return super().start(False)
