import sys
import os
from pathlib import Path
import requests

import pandas as pd
import numpy as np

home = str(Path.home())

sys.path.insert(0,"%s"%home)

from ranking_toolbox import pyrankability
from RPLib.pyrplib import base

pd.set_option('display.max_colwidth', None)

if len(sys.argv) < 3:
    print("Usage: python create_colley_card.py <D dataset id> <dataset id>")
    exit(0)

#group = sys.argv[1]
source_dataset_id = int(sys.argv[1])
dataset_id = int(sys.argv[2])
result_path = f'{dataset_id}_colley_card.json'#sys.argv[2]

df = pd.read_csv(
        "https://raw.githubusercontent.com/IGARDS/RPLib/master/data/dataset_tool_Ds.tsv",sep='\t')

dataset = df.set_index('Dataset ID').loc[dataset_id]
print(dataset)
file_path = dataset['Link']
d = requests.get(file_path).json()
D = pd.DataFrame(d["D"]).fillna(0)
    
print(D.shape)

# Remove anything that has no information
sums1 = D.sum(axis=0)
sums2 = D.sum(axis=1)
mask = sums1 + sums2 != 2*np.diag(D)
D = D.loc[mask,mask]

# We will construct an instance to store our findings
instance = base.ColleyCard()
instance.D = D
instance.source_dataset_id = source_dataset_id
instance.dataset_id = dataset_id

linked = 

colleyMatrix,b, indirect_colleyMatrix, indirect_b = pyrankability.construct.colley_matrices(linked)
ranking, r, perm = pyrankability.rank.ranking_from_matrices(colleyMatrix, b)

first_solution = ranking

instance.centroid_x = 

# Add what we have found to our instance
instance.add_solution(first_solution)

# Now we will see if there are multiple optimal solutions
    # how is this done for Colley?

print('Writing to',result_path)
instance.to_json(result_path)
