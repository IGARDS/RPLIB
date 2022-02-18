# Base Functionality for Reading and Processing
import os
import json
import requests

import pandas as pd

from abc import ABC, abstractmethod

from . import style
 
class Unprocessed(ABC):
    def __init__(self,dataset_id,links):
        self.dataset_id = dataset_id
        self.links = links
        
    @abstractmethod
    def load(self,options={}):
        pass
    
    @abstractmethod
    def data(self):
        pass
    
    @abstractmethod
    def view(self):
        pass
    
class Processed(Unprocessed):
    def __init__(self):
        self._instance = pd.Series([None,None,None,None,None,None],
                                   index=["data","type","short_type","source_dataset_id","dataset_id","command"])
        
    def to_json(self):
        return self._instance.to_json()
       
    @property
    def data(self):
        return self._instance['data']
       
    @data.setter
    def data(self, data):
        self._instance['data'] = data
        
    @property
    def type(self):
        return self._instance['type']
       
    @type.setter
    def type(self, t):
        self._instance['type'] = t
        
    @property
    def short_type(self):
        return self._instance['short_type']
       
    @short_type.setter
    def short_type(self, t):
        self._instance['short_type'] = t
        
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
        
    @staticmethod
    @abstractmethod
    def from_json(file):
        pass
    
    @abstractmethod
    def size_str(self):
        pass

class ProcessedD(Processed):
    def __init__(self):
        self._instance = pd.Series([None,None,None,None,None,None],
                                   index=["data","type","short_type","source_dataset_id","dataset_id","command"])
        
    def load(self,options={}):
        if type(self._instance['data']) != pd.DataFrame:
            self._instance['data'] = pd.DataFrame(self._instance['data'])
        return self
        
    @staticmethod
    def from_json(file):
        try:
            contents = json.loads(open(file).read())
        except:
            link = file # Try to see if this is a link instead of a file
            contents = requests.get(link).json()
        obj = ProcessedD()
        obj._instance = pd.Series(contents)
        return obj
    
    def size_str(self):
        return ",".join([str(i) for i in self.data.shape])
    
    def view(self):
        return style.get_standard_data_table(self.data.reset_index(),"D")
    
    
class ProcessedGames(Processed):
    def __init__(self):
        self._instance = pd.Series([None,None,None,None,None,None],
                                   index=["data","type","short_type","source_dataset_id","dataset_id","command"])
        
    def load(self,options={}):
        if type(self._instance['data']) == list: # first load from JSON
            games,teams = self._instance['data']
            if type(games) != pd.DataFrame:
                self._instance['data'] = (pd.DataFrame(games).T,teams)
            if type(teams) != list:
                self._instance['data'] = (games,list(teams))
        
        return self
    
    def size_str(self):
        return "("+",".join([str(i) for i in self.data[0].shape])+"),"+str(len(self.data[1]))
        
    @staticmethod
    def from_json(file):
        try:
            contents = json.loads(open(file).read())
        except:
            link = file # Try to see if this is a link instead of a file
            contents = requests.get(link).json()
        obj = ProcessedGames()
        obj._instance = pd.Series(contents)
        return obj
    
    def view(self):
        return style.get_standard_data_table(self.data.reset_index(),"games")
  