import os
import sys
from pathlib import Path
import json

import numpy as np

home = str(Path.home())

RPLIB_DATA_PREFIX = os.environ.get("RPLIB_DATA_PREFIX")

if RPLIB_DATA_PREFIX is None: # Set default
    RPLIB_DATA_PREFIX=f'{home}/RPLib/data'
    
try:
    import pyrankability as pyrankability
    import pyrplib as pyrplib
except:
    print('Looking for packages in home directory')
    sys.path.insert(0,f"{home}") # Add the home directory relevant paths to the PYTHONPATH
    sys.path.insert(0,f"{home}/ranking_toolbox") # Add the home directory relevant paths to the PYTHONPATH
    sys.path.insert(0,f"{home}/RPLib") # Add the home directory relevant paths to the PYTHONPATH
    import pyrankability
    import pyrplib

import pandas as pd

usage = "Usage: python load_unprocessed.py <id>"
if len(sys.argv) < 2:
    print(usage)
    exit(0)
        
dataset_id = int(sys.argv[1])

data = pyrplib.data.Data(RPLIB_DATA_PREFIX)

dataset = data.load_unprocessed(dataset_id)

print(dataset)

print(len(dataset.data()))