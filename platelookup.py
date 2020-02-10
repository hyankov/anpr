"""
Description
--
License plate lookup.
"""

# System imports
import functools
from typing import Any, Dict

# Local imports
from threadable import WorkerPipe


class PlateLookup(WorkerPipe):
    channel_plate_info = "channel_plate_info"

    @functools.lru_cache
    def _lookup(self, plate: str) -> Dict[str, Any]:
        """
        Description
        --
        Cached lookup

        Parameters
        --
        - plate - the plate number

        Returns
        --
        A dictionary of plate properties.
        """

        if not plate:
            raise ValueError("plate is required")

        # TODO: Lookup and populate
        return {
            "Stolen": False,
            "VIN": "Whatever VIN",
            "Year": 2005
        }

    def _process_input_job(self, input_job: Any) -> Dict[str, Any]:
        """
        Description
        --
        Looks up a plate number.

        Parameters
        --
        - input_job - license plate number to lookup.

        Returns
        --
        License plate info.
        """

        if input_job:
            info = self._lookup(input_job)
            return {self.channel_plate_info: info}
