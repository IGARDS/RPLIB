import sys
import os
from pathlib import Path

import pandas as pd
import numpy as np

import importlib

home = str(Path.home())

sys.path.insert(0,"%s"%home)

from RPLib.pyrplib import base

if len(sys.argv) < 3:
    print("Usage: python create_D_from_lolib_D.py <source_dataset_id> <dataset_id>")
    exit(0)

#group = sys.argv[1]
source_dataset_id = sys.argv[1]
dataset_id = sys.argv[2]
result_path = f'{dataset_id}_D.json'#sys.argv[2]

#df = pd.read_csv(
#        "https://raw.githubusercontent.com/IGARDS/RPLib/master/data/dataset_tool_datasets.tsv",sep='\t')
df = pd.read_csv(
        "../dataset_tool_datasets.tsv",sep='\t')

dataset = df.set_index('Dataset ID').loc[source_dataset_id]
data_files = dataset['Download links'].split(",")

provenance = dataset['Data provenance'].split("/")[-1][:-3]

load_lib = importlib.import_module(f"RPLib.pipelines.{provenance}")
func_name = os.path.basename(__file__).replace("create","load")[:-3] # the name of this file is the same name as the function to run
print(func_name)
func = getattr(load_lib, func_name)

print("\n".join(data_files))
D = func(data_files[0])

print("Removing any rows + columns without information")
print("Shape before",D.shape)
# Remove anything that has no information
sums1 = D.sum(axis=0)
sums2 = D.sum(axis=1)
mask = sums1 + sums2 != 2*np.diag(D)
D = D.loc[mask,mask]
print("Shape after",D.shape)

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
