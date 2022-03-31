import os
import sys
import json

import numpy as np
import pandas as pd

import scipy.linalg

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

def weakdomplusnoise(n, percentnoise,low=0,high=1):
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