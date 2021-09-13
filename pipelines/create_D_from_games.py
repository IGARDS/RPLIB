import sys
import os
from pathlib import Path

import pandas as pd
import numpy as np

home = str(Path.home())

sys.path.insert(0,"%s"%home)

from ranking_toolbox import pyrankability

if len(sys.argv) < 3:
    print("Usage: python create_D_from_games.py <dataset_id> <outfile>")
    exit(0)

#group = sys.argv[1]
dataset_id = sys.argv[1]
result_path = sys.argv[2]

df = pd.read_csv(
        "../data/dataset_tool_datasets.tsv",sep='\t')

dataset = df.set_index('Dataset ID').loc[dataset_id]
data_files = dataset['Download links'].split(",")

provenance = dataset['Data provenance'].split("/")[-1][:-3]

import importlib

load_lib = importlib.import_module(f"RPLib.pipelines.{provenance}")
func_name = os.path.basename(__file__).replace("create","load")[:-3]
func = getattr(load_lib, func_name)

games,teams = func(data_files[0],data_files[1],data_files[2])

trans = pyrankability.transformers.ComputeDTransformer()
trans.fit(games)
D,ID = trans.transform(games)
D = D.loc[teams,teams]
ID = ID.loc[teams,teams]

print(D)

print('Writing to',result_path)
D.to_csv(result_path)
#open(result_path,'w').write(instance.to_json())
