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

usage = "Usage: python copy_modify_processed.py <simulate|save> <copy_ids> <command_pattern> <command_replacement> [<command_pattern> <command_replacement>]"
if len(sys.argv) < 5:
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

if sys.argv[1] == "save":
    save = True
elif sys.argv[1] == "simulate":
    save = False
else:
    print(usage)
    exit(0)

processed_dataset_ids = get_ids(sys.argv[2].split(","))
patterns = []
replacements = []
pattern_replacement = sys.argv[3:]
if len(pattern_replacement) % 2 == 0 and len(pattern_replacement) == 0:
    print(usage)
    exit(0)
for j in range(len(pattern_replacement)//2):
    patterns.append(pattern_replacement[2*j])
    replacements.append(pattern_replacement[2*j+1])

config = pyrplib.config.Config(RPLIB_DATA_PREFIX)

datasets_df = config.datasets_df
processed_datasets_df = config.processed_datasets_df

datasets_df.set_index('Dataset ID',inplace=True)

processed_datasets_df.set_index('Dataset ID',inplace=True)

new_id = max(processed_datasets_df.index)+1

import importlib
from datetime import datetime
import re

for dataset_id in processed_dataset_ids:
    dataset = processed_datasets_df.loc[dataset_id]
    new_dataset = dataset.copy()
    new_dataset.name = new_id
    command = dataset['Command']
    options = dataset['Options']
    new_command = command
    for i in range(len(patterns)):
        new_command = re.sub(patterns[i],replacements[i],new_command)
    new_dataset['Command'] = new_command
    new_dataset['Last Processed Datetime'] = ''
    print("Before:")
    print(command)
    print("After:")
    print(new_command)

    if save:
        processed_datasets_df.loc[new_dataset.name] = new_dataset
        
    new_id += 1
        
config.save_processed_datasets()
