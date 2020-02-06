"""
Description
--
License plate scanner on the go.

Author
--
Hristo Yankov
"""

from typing import NamedTuple
from typing import Any, Dict
from numpy import ndarray


class LicensePlateInfo(NamedTuple):
    plate: str
    frame: ndarray = None
    props: Dict[str, Any] = {}
