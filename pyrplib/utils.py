#!/usr/bin/env python
# coding: utf-8

# # A Utility Library for Rankability Problems

# In[ ]:


import pandas as pd
import itertools


# ## Problem 1

# In[ ]:


# Constructs a dataframe from selected parameters
# columns is a dictionary of form {col_name: col_value}
def get_sel_df(columns):
    sel_df = pd.DataFrame(columns=list(columns.keys()))
    c = 0
    print(list(columns.values()))
    for values in itertools.product(*columns.values()):
        print(values)
        sel_df = sel_df.append(pd.Series(values, index=sel_df.columns, name=c))
        c += 1

    return sel_df

