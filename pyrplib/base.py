# Base Functionality for Reading and Processing
import os
from io import StringIO
import json

import pandas as pd

# Python program showing the use of
# @property
  
class LOPCard:
    def __init__(self):
        self._instance = pd.Series([None,None,set(),None,None,None,None],
                                   index=["D","obj","solutions","max_tau_solutions",
                                          "centroid_x","outlier_solution","dataset_id"])
        
    def to_json(self):
        return self._instance.to_json()
       
    @property
    def D(self):
        return self._instance['D']
       
    @D.setter
    def D(self, D):
        self._instance['D'] = D
        
      
        
    @property
    def obj(self):
        return self._instance['obj']
       
    @obj.setter
    def obj(self, obj):
        self._instance['obj'] = obj
        
    @property
    def dataset_id(self):
        return self._instance['dataset_id']
       
    @obj.setter
    def dataset_id(self, id):
        self._instance['dataset_id'] = id
        
    @property
    def centroid_x(self):
        return self._instance['centroid_x']
       
    @centroid_x.setter
    def centroid_x(self, centroid_x):
        self._instance['centroid_x'] = centroid_x
        
    @property
    def outlier_solution(self):
        return self._instance['outlier_solution']
       
    @outlier_solution.setter
    def outlier_solution(self, outlier_solution):
        self._instance['outlier_solution'] = outlier_solution
        
    @property
    def solutions(self):
        return self._instance['solutions']
        
    def add_solution(self,sol):
        if type(sol) != tuple:
            sol = tuple(sol)
        self._instance['solutions'].add(sol)

def read_instance(file):
    lines = open(f"{file}").read().strip().split("\n")[1:]
    data_str = ("\n".join([line.strip() for line in lines])).replace(" ",",")
    df = pd.read_csv(StringIO(data_str),header=None)
    return df


