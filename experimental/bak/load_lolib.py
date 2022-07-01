import sys
from pathlib import Path

import pandas as pd
import numpy as np

home = str(Path.home())

sys.path.insert(0,"%s"%home)

from lolib_study import base

def load_D_from_lolib_D(link_to_lolib_D):
    D = base.read_instance_url(link_to_lolib_D)
    return D