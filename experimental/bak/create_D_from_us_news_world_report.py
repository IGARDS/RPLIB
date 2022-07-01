import sys
import os
from pathlib import Path

import pandas as pd
import numpy as np

from ranking_toolbox import pyrankability
from RPLib.pyrplib import base

if len(sys.argv) < 6:
    print("Usage: python create_D_from_us_news_world_report.py <source_dataset_id> <dataset_id> <year> <colleges> <columns>")
    exit(0)

source_dataset_id = sys.argv[1]
dataset_id = sys.argv[2]
year = int(sys.argv[3])
colleges = list(pd.read_csv(sys.argv[4],header=None)[0])
columns = list(pd.read_csv(sys.argv[5],header=None)[0])

result_path = f'{dataset_id}_D.json'

exec(open('../config_dev.py').read())

df = datasets_df

dataset = df.set_index('Dataset ID').loc[source_dataset_id]
data_files = dataset['Download links'].split(",")

provenance = dataset['Data provenance'].split("/")[-1][:-3]

import importlib

load_lib = importlib.import_module(f"RPLib.pipelines.{provenance}")
func_name = os.path.basename(__file__).replace("create","load")[:-3] # the name of this file is the same name as the function to run
print(func_name)
func = getattr(load_lib, func_name)

print("\n".join(data_files))
games,teams = func(data_files[0],data_files[1],data_files[2])

trans = pyrankability.transformers.ComputeDTransformer()
trans.fit(games)
D,ID = trans.transform(games)
D = D.reindex(index=teams,columns=teams)
ID = ID.reindex(index=teams,columns=teams)

print(D)

D_info = base.DInfo()
D_info.D = D
# "D_type","source_dataset_id","dataset_id","command"
D_info.D_type = "Count"
D_info.source_dataset_id = source_dataset_id
D_info.dataset_id = dataset_id
D_info.command = " ".join(sys.argv)

print('Writing to',result_path)
open(result_path,'w').write(D_info.to_json())
#D.to_csv(result_path)
