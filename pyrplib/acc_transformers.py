#!/usr/bin/env python
# coding: utf-8
# %%


import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import itertools


# %%


import sys
from pathlib import Path
home = str(Path.home())

import pyrankability


# %%


# TODO: add in more options if we want
direct_thress = [0] # might be of interest to see how sensitive to preprocessing, but not now
spread_thress = [0]
weight_indirects = [0,0.1,0.5,1]
methods = ['Massey','Colley']
sel_df = pd.DataFrame(columns=['direct_thres','spread_thres','weight_indirect','Method'])
c = 0
for dt,st,wi,method in itertools.product(direct_thress,spread_thress,weight_indirects,methods):
    sel_df = sel_df.append(pd.Series([dt,st,wi,method],index=sel_df.columns,name=c))
    c+=1

sel_df


# %%


# Transforms dataframe from product of input columns
class ParameterProductTransformer( BaseEstimator, TransformerMixin ):
    # columns is a dictionary of form {col_name: col_value}
    def __init__(self,columns):
        self.columns = columns
        
    #Return self nothing else to do here
    def fit( self, X, y = None  ):
        return self
    
    def transform(self, X, y = None ):
        sel_df = pd.DataFrame(columns=list(self.columns.keys()))
        c = 0
        for values in itertools.product(list(self.columns.values())):
            sel_df = sel_df.append(pd.Series(list(values), index=sel_df.columns, name=c))
            c += 1
            
        return sel_df


# %%
#columns = {'direct_thres': [0], 'spread_thres': [0], 'weight_indirect': [0,0.1,0.5,1], 'Method': ['Massey','Colley']}
#for values in itertools.product(list(columns.values())):
#    print(values)




# %%
