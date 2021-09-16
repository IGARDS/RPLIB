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
    print("Usage: python create_lop_card.py <D dataset id> <outfile>")
    exit(0)

#group = sys.argv[1]
dataset_id = sys.argv[1]
result_path = sys.argv[2]

df = pd.read_csv(
        "https://raw.githubusercontent.com/IGARDS/RPLib/master/data/dataset_tool_datasets.tsv",sep='\t')

dataset = df.set_index('Dataset ID').loc[dataset_id]
data_files = dataset['Download links'].split(",")
provenance = dataset['Data provenance'].split("/")[-1][:-3]

file_path = data_files[0]
D = pd.read_csv(data_files[0],index_col=0).fillna(0)
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
solution = pd.Series([cont,fix_x,delta,details],index=["cont","fix_x","delta","details"],name=0)
orig_sol_x = details['x']
orig_obj = details['obj']

# Add what we have found to our instance
instance.obj = orig_obj
instance.add_solution(solution['details']['P'][0])

# Now we will see if there are multiple optimal solutions
try:
    cont = False
    other_delta,other_detail = pyrankability.search.solve_any_diff(D,orig_obj,orig_sol_x,method='lop')
    other_solution = pd.Series([cont,orig_obj,orig_sol_x,delta,details],index=["cont","orig_obj","orig_sol_x","delta","details"],name=1)
    print(other_solution['details']['P'])
    instance.add_solution(other_solution['details']['P'][0])
    print('Found multiple solutions for %s'%file_path)
except:
    print('Cannot find multiple solutions for %s (or another problem occured)'%file_path)

if len(instance.solutions) > 1: # Multiple optimal
    outlier_deltas,outlier_details = pyrankability.search.solve_min_tau(D,centroid_x,orig_sol_x,method='lop')
    instance.add_solution(outlier_details['P'][0])
    instance.outlier_solution = outlier_details['P'][0]

# solutions = pd.concat([solution,other_solution],axis=1).T
# record = pd.Series({"group":group,"file":file,"D":D,"mask":mask,"method":"lop","solutions":solutions})

print('Writing to',result_path)
open(result_path,'w').write(instance.to_json())
