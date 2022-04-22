from enum import Enum
import os

class Method(Enum):
    LOP = 0
    HILLSIDE = 1
    MASSEY = 2
    COLLEY = 3

RPLIB_DATA_PREFIX = os.environ.get("RPLIB_DATA_PREFIX")