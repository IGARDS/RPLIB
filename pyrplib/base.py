# Base Functionality for Reading and Processing
import os
import json
import requests

import pandas as pd

class DInfo:
    def __init__(self):
        self._instance = pd.Series([None,None,set(),None,None],
                                   index=["D","D_type","source_dataset_id","dataset_id","command"])
        
    def to_json(self):
        return self._instance.to_json()
       
    @property
    def D(self):
        return self._instance['D']
       
    @D.setter
    def D(self, D):
        self._instance['D'] = D
        
    @property
    def D_type(self):
        return self._instance['D_type']
       
    @D_type.setter
    def D_type(self, D_type):
        self._instance['D_type'] = D_type
        
    @property
    def source_dataset_id(self):
        return self._instance['source_dataset_id']
       
    @source_dataset_id.setter
    def source_dataset_id(self, id):
        self._instance['source_dataset_id'] = id
        
    @property
    def dataset_id(self):
        return self._instance['dataset_id']
       
    @dataset_id.setter
    def dataset_id(self, id):
        self._instance['dataset_id'] = id
        
    @property
    def command(self):
        return self._instance['command']
       
    @command.setter
    def command(self, command):
        self._instance['command'] = command
  
class LOPCard:
    def __init__(self):
        self._instance = pd.Series([None,None,set(),None,None,None,None],
                                   index=["D","obj","solutions","max_tau_solutions",
                                          "centroid_x","outlier_solution","dataset_id"])
        
    def to_json(self,file):
        self._instance.to_json(file,orient='columns')
       
    @property
    def D(self):
        return self._instance['D']
       
    @D.setter
    def D(self, D):
        self._instance['D'] = D
        
    @property
    def source_dataset_id(self):
        return self._instance['source_dataset_id']
       
    @source_dataset_id.setter
    def source_dataset_id(self, id):
        self._instance['source_dataset_id'] = id
        
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
    def centroid_solution(self):
        return self._instance['centroid_solution']
       
    @centroid_solution.setter
    def centroid_solution(self, centroid_solution):
        self._instance['centroid_solution'] = centroid_solution
        
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
        
    @staticmethod
    def from_json(file):
        try:
            contents = json.loads(open(file).read())
        except:
            link = file # Try to see if this is a link instead of a file
            contents = requests.get(link).json()
        obj = LOPCard()
        obj._instance = pd.Series(contents)
        return obj
                            
# almost exact same as above^ 
# not sure if LOPCard and ColleyCard need same functionality for almost everything and should just inherit from some 'Card' class
class ColleyCard:
    def __init__(self):
        self._instance = pd.Series([None,None,set(),None,None,None,None],
                                   index=["D","obj","solutions","max_tau_solutions",
                                          "centroid_x","outlier_solution","dataset_id"])
        
    def to_json(self,file):
        self._instance.to_json(file,orient='columns')
       
    @property
    def D(self):
        return self._instance['D']
       
    @D.setter
    def D(self, D):
        self._instance['D'] = D
        
    @property
    def source_dataset_id(self):
        return self._instance['source_dataset_id']
       
    @source_dataset_id.setter
    def source_dataset_id(self, id):
        self._instance['source_dataset_id'] = id
        
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
        
    @staticmethod
    def from_json(file):
        try:
            contents = json.loads(open(file).read())
        except:
            link = file # Try to see if this is a link instead of a file
            contents = requests.get(link).json()
        obj = ColleyCard()
        obj._instance = pd.Series(contents)
        return obj
                         