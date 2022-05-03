import os
import sys
import json

import numpy as np
import pandas as pd

RPLIB_DATA_PREFIX = os.environ.get("RPLIB_DATA_PREFIX")

if RPLIB_DATA_PREFIX is None: # Set default
    raise Exception("RPLIB_DATA_PREFIX must be set")
print("RPLIB_DATA_PREFIX",RPLIB_DATA_PREFIX)

try:
    import pyrankability as pyrankability
    import pyrplib as pyrplib
except:
    print('Looking for packages relative to data prefix')
    sys.path.insert(0,f"{RPLIB_DATA_PREFIX}/../../ranking_toolbox") 
    sys.path.insert(0,f"{RPLIB_DATA_PREFIX}/..")  
    import pyrankability
    import pyrplib

if len(sys.argv) < 2:
    print("Usage: python process.py <comma separated processed dataset ids (comma separated or e.g., 3:8)>")
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
processed_dataset_ids = get_ids(sys.argv[1].split(",")) #[int(i) for i in sys.argv[1].split(",")]

config = pyrplib.data.Data(RPLIB_DATA_PREFIX)

datasets_df = config.datasets_df
processed_datasets_df = config.processed_datasets_df

datasets_df.set_index('Dataset ID',inplace=True)

processed_datasets_df.set_index('Dataset ID',inplace=True)

import importlib
from datetime import datetime

for dataset_id in processed_dataset_ids:
    dataset = processed_datasets_df.loc[dataset_id]
    index = dataset['Index']
    print(dataset)
    source_dataset_id = dataset['Source Dataset ID']
    print(source_dataset_id,"->",dataset_id)
    links = datasets_df.loc[source_dataset_id,'Download links']
    loader = datasets_df.loc[source_dataset_id,'Loader']
    command = dataset['Command']
    options = dataset['Options']
    if type(options) == str:
        options = json.loads(options)
        print("Loaded options:")
        print(json.dumps(options, indent=2))

    collection = dataset.loc['Collection']
    loader_lib = ".".join(loader.split(".")[:-1])
    cls_str = loader.split(".")[-1]
    load_lib = importlib.import_module(f"pyrplib.{loader_lib}")
    cls = getattr(load_lib, cls_str)
    unprocessed = cls(source_dataset_id,links).load()
    #funcs = command.split("...")[0].split("(")[:-1]
    data = unprocessed.data()
    command = command.replace("transformers.","pyrplib.transformers.")
    exec(f"data = {command}")
    
    # datetime object containing current date and time
    now = datetime.now()

    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print("date and time =", dt_string)

    data.source_dataset_id = source_dataset_id
    data.dataset_id = dataset_id
    data.command = command

    processed_datasets_df.loc[dataset_id,'Last Processed Datetime'] = dt_string

    result_path = f"../data/{collection}/{dataset_id}.json"
    print('Writing to',result_path)
    open(result_path,'w').write(data.to_json())
        
config.save_processed_datasets()
