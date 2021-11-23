import sys
import os
from pathlib import Path

import pandas as pd
import numpy as np

home = str(Path.home())

sys.path.insert(0,"%s"%home)

from ranking_toolbox import pyrankability
from RPLib.pyrplib import base

if len(sys.argv) < 3:
    print("Usage: python create_matrices_from_games.py <source_dataset_id> <dataset_id>")
    exit(0)

#group = sys.argv[1]
source_dataset_id = sys.argv[1]
dataset_id = sys.argv[2]
result_path = f'{dataset_id}_colley_matrices.json'#sys.argv[2]

df = pd.read_csv(
        "https://raw.githubusercontent.com/IGARDS/RPLib/master/data/dataset_tool_datasets.tsv",sep='\t')

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

map_func = lambda linked: pyrankability.construct.colley_matrices(linked,direct_thres=0,spread_thres=0)
colley_matrix,colley_b,indirect_colley_matrix,indirect_colley_b = pyrankability.construct.map_vectorized(games,map_func)
#ranking1,r1,perm1 = pyrankability.rank.ranking_from_matrices(colley_matrix.fillna(0),colley_b.fillna(0))

matrices_info = base.MatricesInfo()
matrices_info.matrix = colley_matrix
matrices_info.b = colley_b
matrices_info.source_dataset_id = source_dataset_id
matrices_info.dataset_id = dataset_id
matrices_info.command = " ".join(sys.argv)

print('Writing to',result_path)
open(result_path,'w').write(matrices_info.to_json())
#D.to_csv(result_path)
