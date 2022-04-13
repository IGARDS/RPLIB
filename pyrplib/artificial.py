import os
import sys
import json

import numpy as np
import pandas as pd

import scipy.linalg

import inspect

def cyclic(n):
    """
    Create a simple cycle D matrix of size n x n.
    """
    D=pd.DataFrame(np.zeros((n,n)),dtype=int) # initialize D as an empty graph 
    for i in range(n):
        D.iloc[i,i+1] = 1
    D.iloc[n-1,0] = 1
    return D

def addmossimple(D,start_index,end_index):
    """
    For a binary matrix D, create simple multiple optimal solutions in the range of teams specified.
    Indices are inclusive.
    """
    index = D.index
    columns = D.columns
    D = D.copy().values
    assert end_index > start_index
    for i in range(start_index,end_index+1):
        for j in range(i+1,end_index+1):
            total = D[i,j] + D[j,i]
            D[i,j] = total
            D[j,i] = total
    return pd.DataFrame(D,index=index,columns=columns)

def domfromranking(n,r,ngames,upset_func=lambda r1,r2: np.exp(r2) / np.sum(np.exp([r1,r2])) >= np.random.uniform()):
    """
    DOM matrix from ranking

    Simulates win/loss of individual games using the ranking vector (r) and the upset function. 
    The upset function must take two rankings r1 and r2. r1 > r2. This function must return
    True/False depending on whether an upset occurred. 
    """
    D = pd.DataFrame(np.zeros((n,n)),index=r.index,columns=r.index,dtype=int)
    for g in range(ngames):
        while True:
            team1,team2 = np.random.choice(r.index,size=2)
            if team1 != team2:
                break
        r1,r2 = r[team1],r[team2]
        if r1 < r2:
            r2,r1 = r1,r2
            team2,team1 = team1,team2
        upset = upset_func(r1,r2)
        if upset:
            D.loc[team2,team1] += 1
        else:
            D.loc[team1,team2] += 1
    return D

def example_get_create_options2():
    """
    Example set of options to be paired with example_create2 function.
    """
    return {
        "number_matrices":10,
        "number_of_rows_columns": 20,
        "num_games":1000
    }

def example_get_create_options():
    """
    Example set of options to be paired with example_create function.
    """
    return {
        "number_matrices":10,
        "number_of_rows_columns": 20,
        "threshold":3,
        "num_games":1000
    }

def example_create(options=example_get_create_options()):
    """
    Example create function. These functions must return a dominance (D) matrix that is a pandas dataframe. 
    Options is a dictionary. There is one required key/value which is the number_of_rows_columns. 
    It may also have additional arguments.
    """
    assert type(options) == dict
    r = pd.Series(np.arange(options['number_of_rows_columns'],0,-1))

    D = domfromranking(options['number_of_rows_columns'],r,options['num_games'],
                              upset_func=lambda r1,r2: (abs(r1-r2) <= options['threshold']) and np.random.uniform() > 0.5)
    return D

def example_create3(options):
    """
    Example create function. These functions must return a dominance (D) matrix that is a pandas dataframe. 
    Options is a dictionary. There is one required key/value which is the number_of_rows_columns. 
    It may also have additional arguments.
    """
    assert type(options) == dict
    D = domplusnoise(options['number_of_rows_columns'],options['percentage'],options['low'],options['high'])
    if options['percent_links_to_remove'] > 0:
        D = removelinks(D,options['percent_links_to_remove'])
    if options['make_unweighted']:
        D = unweighted(D)
    return D

def example_get_create_options3():
    return {
        "number_matrices":10,
        "number_of_rows_columns": 20,
        "low":0,
        "high":5,
        "percentage":30,
        "percent_links_to_remove":10,
        "make_unweighted":False,
    }

def example_create2(options=example_get_create_options2()):
    """
    Example create function. These functions must return a dominance (D) matrix that is a pandas dataframe. 
    Options is a dictionary. There is one required key/value which is the number_of_rows_columns. 
    It may also have additional arguments.
    """
    assert type(options) == dict
    r = pd.Series(np.arange(options['number_of_rows_columns'],0,-1))

    D = domfromranking(options['number_of_rows_columns'],r,options['num_games'],upset_func=lambda r1,r2: np.exp(r2) / np.sum(np.exp([r1,r2])) >= np.random.uniform())
    return D

def create_dataset(create_func,options):
    """
    Create a dataset using a create function and a function to generate the options used.

    See example create_func and get_create_options_func
    """
    assert type(options) == dict
    Ds = pd.Series([]*options['number_matrices'],dtype=object)#[pd.DataFrame(np.zeros((number_of_rows_columns,number_of_rows_columns)))])
    for i in range(options['number_matrices']):
        Ds[i] = create_func(options)

    create_code = inspect.getsource(create_func)

    dataset = pd.Series(options)
    dataset["Create code"] = create_code
    dataset["Ds"] = Ds
    return dataset

def create_dataset_manual(D_matrices,options,create_code="manual"):
    """
    Create a dataset by manually passing the D matrices as a list.
    The options are not used in any way. They are here if you want to include them.
    """
    assert type(options) == dict
    Ds = pd.Series([]*len(D_matrices),dtype=object)#[pd.DataFrame(np.zeros((number_of_rows_columns,number_of_rows_columns)))])
    for i in range(len(D_matrices)):
        Ds[i] = D_matrices[i]

    dataset = pd.Series(options)
    dataset["Create code"] = create_code
    dataset["Ds"] = Ds
    return dataset

def addnoise(D,percentnoise,low=0,high=1):
    """
    ADD NOISE

    Function replaces random off diagonal elements in D with values from low to high
    """
    assert type(D) == np.ndarray
    assert percentnoise >= 0 and percentnoise <= 100
    assert type(low) == int
    assert type(high) == int
    assert D.shape[0] == D.shape[1]
    n = len(D)
    N=np.random.randint(low=low,high=high+1, size=n*n) # add random integers between 1 and n in random locations
    row1,col1= np.triu_indices(n,k=1)
    row2,col2 = np.tril_indices(n,k=-1)
    row = np.hstack([row1,row2])
    col = np.hstack([col1,col2])

    count = round(n**2*0.01*percentnoise)
    winners = np.random.choice(len(row), count)
    row_winners,col_winners = row[winners],col[winners]
    D[row_winners,col_winners] = N[:count]

    return D

def unweighted(D):
    """
    CONVERT TO UNWEIGHTED

    Function returns an unweighted version of D
    """
    assert type(D) == pd.DataFrame
    D = D.copy()
    rows,cols = np.where(D != 0)
    D.values[rows,cols] = 1
    return D

def removelinks(D,percent):
    """
    CONVERT TO UNWEIGHTED

    Function returns a modified version of D with percent of nonzero links removed
    """
    assert type(D) == pd.DataFrame
    assert percent >= 0 and percent <= 100
    D = D.copy()
    row,col = np.where(D != 0)

    count = int(np.ceil(len(row)*0.01*percent))
    winners = np.random.choice(len(row), count)
    row_winners,col_winners = row[winners],col[winners]
    D.values[row_winners,col_winners] = 0

    return D

def emptyplusnoise(n,percentnoise,low=0,high=3):
    """
    EMPTY + NOISE

    Function starts with an empty graph and adds some amount of noise.

    Input: n = number of rows/cols in D matrix
    percentnoise = integer between 1 and n^2 representing the
    percentage of noise to add to D hillside, e.g., 
    if percentnoise = 10, then 10% of the n^2 elements will be noise

    Example: 'D = emptyplusnoise(6,20)' creates a 6 by 6 matrix with 20% noise
    added to the empty graph
    """
    D=pd.DataFrame(np.zeros((n,n)),dtype=int) # initialize D as an empty graph     
    addnoise(D.values,percentnoise,low=low,high=high)
    return D

def hillsideplusnoise(n, percentnoise, low=1,high=5):
    """
    HILLSIDE + NOISE

    Starts with a perfect hillside graph and then randomly perturbs the matrix at user specified percentage. 

    Input: n = number of rows/cols in D matrix
          percentnoise = integer between 1 and n^2 representing the
                        percentage of noise to add to D hillside, e.g., 
                        if percentnoise = 10, then 10% of the n^2
                        elements will be noise
    Example: 'D = hillsideplusnoise(6,20)' creates a 6 by 6 matrix with 20% noise
              added to the hillside graph
    """
    D = pd.DataFrame(np.triu(scipy.linalg.toeplitz(np.arange(n))),dtype=int) # initialize D as a graph in hillside form.
    addnoise(D.values,percentnoise,low=low,high=high)
    return D

def domplusnoise(n, percentnoise,low=0,high=1):
    """
    function creates a dominance graph and adds noise. 

    Input: n = number of rows/cols in D matrix
          percentnoise = integer between 1 and n^2 representing the
                        percentage of noise to add to D domgraph, e.g., 
                        if percentnoise = 10, then 10% of the n^2
                        elements will be noise
    Example: 'D = domplusnoise(6,20)' creates a 6 by 6 matrix with 20% noise
                added to the dominance graph
    """
    D = pd.DataFrame(np.triu(high*np.ones((n, n)), 1),dtype=int) # initialize D as perfect dominance matrix
    addnoise(D.values,percentnoise,low=low,high=high)
    return D

def weakdomplusnoise(n, percentnoise,low=0,high=1,):
    """
    function creates a weak dominance graph and adds noise. 

    Input: n = number of rows/cols in D matrix
          percentnoise = integer between 1 and n^2 representing the
                        percentage of noise to add to D domgraph, e.g., 
                        if percentnoise = 10, then 10% of the n^2
                        elements will be noise
    Example: 'D = weakdomplusnoise(6,20)' creates a 6 by 6 matrix with 20% noise
                added to the dominance graph
    """
    D = pd.DataFrame(high*np.eye(n+1)[1:,:-1],dtype=int) # initialize D as perfect dominance matrix
    addnoise(D.values,percentnoise,low=low,high=high)
    return D