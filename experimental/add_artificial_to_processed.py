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

usage = "Usage: python add_artificial_to_processed.py <copy_ids> <copy_dataset_id>"
if len(sys.argv) < 3:
    print(usage)
    exit(0)
        
def get_ids(str_ids):
    ids = []
    for i in str_ids:
        if ":" in i:
            s,e = i.split(":")
            s,e = int(s),int(e)
            for j in range(s,e+1):
                ids.append(j)
        else:
            ids.append(int(i))
    return ids

unprocessed_dataset_ids = get_ids(sys.argv[1].split(","))
copy_dataset_id = sys.argv[2]

config = pyrplib.config.Config(RPLIB_DATA_PREFIX)

datasets_df = config.datasets_df
datasets_df.set_index('Dataset ID',inplace=True)

import importlib
from datetime import datetime

for dataset_id in unprocessed_dataset_ids:
    dataset = datasets_df.loc[dataset_id]    
    links = dataset['Download links']
    loader = dataset['Loader']

    loader_lib = ".".join(loader.split(".")[:-1])
    cls_str = loader.split(".")[-1]
    load_lib = importlib.import_module(f"pyrplib.{loader_lib}")
    cls = getattr(load_lib, cls_str)
    unprocessed = cls(dataset_id,links).load()
    df = unprocessed.data()[0]
    for row in df.index:
        for i in range(len(df.loc[row,'Ds'])):
            print("""python copy_modify_processed.py save 109 "loc\[0" "loc[%s" "\['0" "['%s" """%(row,i))