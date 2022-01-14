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

if len(sys.argv) < 2:
    print("Usage: python process.py <comma separated processed dataset ids (comma separated)>")
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

config = pyrplib.config.Config(RPLIB_DATA_PREFIX)

datasets_df = config.datasets_df
processed_datasets_df = config.processed_datasets_df

datasets_df.set_index('Dataset ID',inplace=True)

processed_datasets_df.set_index('Dataset ID',inplace=True)

import importlib
from datetime import datetime

for dataset_id in processed_dataset_ids:
    dataset = processed_datasets_df.loc[dataset_id]
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
    if "base" in loader: # migration check
        loader_lib = ".".join(loader.split(".")[:-1])
        cls_str = loader.split(".")[-1]
        load_lib = importlib.import_module(f"pyrplib.{loader_lib}")
        cls = getattr(load_lib, cls_str)
        unprocessed = cls(source_dataset_id,links).load()
        funcs = command.split("...")[0].split("(")[:-1]
        data = unprocessed.data()
        for func in funcs[::-1]:
            if func == "transformers.count":
                data = pyrplib.transformers.count(*data)
            elif func == "transformers.direct":
                data = pyrplib.transformers.direct(*data)
            elif func == "transformers.indirect":
                data = pyrplib.transformers.indirect(*data)
            elif func == "transformers.process_D":
                data = pyrplib.transformers.process_D(*data)
            elif func == "transformers.features_to_D":
                data = pyrplib.transformers.features_to_D(*data,options=options)
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
