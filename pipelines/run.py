import os
import sys
from pathlib import Path
import json
from datetime import datetime

import numpy as np
import pandas as pd

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

if len(sys.argv) < 2:
    print("Usage: python run.py <method (e.g., lop,hillside,massey,colley)> <ids (comma separated)>")
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

method = sys.argv[1]
method_dataset_ids = get_ids(sys.argv[2].split(",")) #[int(i) for i in sys.argv[1].split(",")]

config = pyrplib.config.Config(RPLIB_DATA_PREFIX)

datasets_df = config.datasets_df
processed_datasets_df = config.processed_datasets_df
if method == 'lop':
    method_datasets_df = config.lop_cards_df

datasets_df.set_index('Dataset ID',inplace=True)
processed_datasets_df.set_index('Dataset ID',inplace=True)
method_datasets_df.set_index('Dataset ID',inplace=True)

for dataset_id in method_dataset_ids:
    dataset = method_datasets_df.loc[dataset_id]
    processed_dataset_id = dataset['Processed Dataset ID']
    processed_dataset = processed_datasets_df.loc[processed_dataset_id]
    print('Processed dataset loaded:')
    print(processed_dataset)
    
    if method == 'lop':
        card = pyrplib.card.LOP().load(dataset_id,dataset['Options'])
        
    card.prepare(processed_dataset)
    card.run()
    
    # datetime object containing current date and time
    now = datetime.now()

    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print("date and time =", dt_string)

    method_datasets_df.loc[dataset_id,'Last Processed Datetime'] = dt_string

    result_path = f"../data/{method}/{dataset_id}.json"
    print('Writing to',result_path)
    open(result_path,'w').write(card.to_json())

if method == 'lop':
    config.save_lop_datasets()
