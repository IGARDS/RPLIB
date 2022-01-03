import sys
import os
from pathlib import Path
import requests

import pandas as pd
import numpy as np
import json

home = str(Path.home())

sys.path.insert(0,"%s"%home)

from ranking_toolbox import pyrankability
from RPLib.pyrplib import base

pd.set_option('display.max_colwidth', None)

if len(sys.argv) < 3:
    print("Usage: python create_lop_card.py <D dataset id> <dataset id>")
    exit(0)

#group = sys.argv[1]
source_dataset_id = int(sys.argv[1])
dataset_id = int(sys.argv[2])
result_path = f'{dataset_id}_lop_card.json'#sys.argv[2]

df = pd.read_csv(
        "../dataset_tool_Ds.tsv",sep='\t')

dataset = df.set_index('Dataset ID').loc[dataset_id]
print(dataset)
file_path = dataset['Link']
try:
    d = requests.get(file_path).json()
except:
    d = json.loads(open(file_path).read())
D = pd.DataFrame(d["D"]).fillna(0)
    
print(D.shape)
#D = base.read_instance(data_files[0])

# Remove anything that has no information
sums1 = D.sum(axis=0)
sums2 = D.sum(axis=1)
mask = sums1 + sums2 != 2*np.diag(D)
D = D.loc[mask,mask]

# We will construct an instance to store our findings
instance = base.LOPCard()
instance.D = D
instance.source_dataset_id = source_dataset_id
instance.dataset_id = dataset_id

# Solve using LP which is faster
delta_lp,details_lp = pyrankability.rank.solve(D,method='lop',cont=True)

# Next threshold numbers close to 1.0 or 0.0 and then convert to a dictionary style that is passed to later functions
orig_sol_x = pyrankability.common.threshold_x(details_lp['x'])
centroid_x = orig_sol_x
instance.centroid_x = centroid_x
# Fix any that can be rounded. This leaves Gurubi a much smaller set of parameters to optimize
fix_x = {}
rows,cols = np.where(orig_sol_x==0)
for i in range(len(rows)):
    fix_x[rows[i],cols[i]] = 0
rows,cols = np.where(orig_sol_x==1)
for i in range(len(rows)):
    fix_x[rows[i],cols[i]] = 1

# Now solve BILP
cont = False
delta,details = pyrankability.rank.solve(D,method='lop',fix_x=fix_x,cont=cont)
orig_sol_x = details['x']
orig_obj = details['obj']
first_solution = details['P'][0]

# Add what we have found to our instance
instance.obj = orig_obj
instance.add_solution(first_solution)

# Now we will see if there are multiple optimal solutions
try:
    cont = False
    other_delta,other_detail = pyrankability.search.solve_any_diff(D,orig_obj,orig_sol_x,method='lop')
    other_solution = other_detail['perm']
    #print(other_solution['details']['P'])
    instance.add_solution(other_solution)
    print('Found multiple solutions for %s'%file_path)
except:
    print('Cannot find multiple solutions for %s (or another problem occured)'%file_path)

if len(instance.solutions) > 1: # Multiple optimal
    #solve_pair(D,D2=None,method=["lop","hillside"][1],minimize=False,min_ndis=None,max_ndis=None,tau_range=None,lazy=False,verbose=False)
    outlier_deltas,outlier_details = pyrankability.search.solve_fixed_cont_x(D,delta,centroid_x,method='lop',minimize=False)
    instance.add_solution(outlier_details['perm'])
    instance.outlier_solution = outlier_details['perm']
    
    centroid_deltas,centroid_details = pyrankability.search.solve_fixed_cont_x(D,delta,centroid_x,method='lop',minimize=True)
    instance.add_solution(centroid_details['perm'])
    instance.centroid_solution = centroid_details['perm']

# solutions = pd.concat([solution,other_solution],axis=1).T
# record = pd.Series({"group":group,"file":file,"D":D,"mask":mask,"method":"lop","solutions":solutions})

print('Writing to',result_path)
instance.to_json(result_path)
