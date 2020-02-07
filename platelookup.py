"""
Description
--
License plate lookup.
"""

# System imports
import functools
from typing import Any, Dict

# Local imports
from threadable import ConsumerProducer


class PlateLookup(ConsumerProducer):
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

    def _consume(self, item: Any) -> Any:
        """
        Description
        --
        Consumes a license plate number.

        Parameters
        --
        - item - license plate number (str)

        Returns
        --
        License plate information.
        """

        if item:
            return self._lookup(item)
