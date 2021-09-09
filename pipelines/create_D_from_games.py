import pandas as pd
import numpy as np

import sys
from pathlib import Path
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

ComputeDTransformer()

import ranking_toolbox.base
import ranking_toolbox.pyrankability


# data_dir = f'{home}/lolib_study/data/'
# results_dir = f'{home}/lolib_study/RPLib/'

# file_path = f'{data_dir}/{group}/{file}'
# result_path = f'{results_dir}/{group}/{file}.json'

D = base.read_instance(file_path)

# Remove anything that has no information
sums1 = D.sum(axis=0)
sums2 = D.sum(axis=1)
mask = sums1 + sums2 != 2*np.diag(D)
D = D.loc[mask,mask]

# We will construct an instance to store our findings
instance = base.LOLibInstance()
instance.D = D

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
