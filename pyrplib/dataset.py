# Base Functionality for Reading and Processing
import os
import json
import requests
import importlib
from abc import ABC, abstractmethod

import pandas as pd

from enum import Enum

from dash import html

from . import style

class UnprocessedType(Enum):
    D = 0
    Games = 1
    Features = 2
    
def load_unprocessed(unprocessed_source_id,datasets_df):
    """Helper function to load unprocessed dataset.

    :param [unprocessed_source_id]: [Unprocessed dataset ID]
    :param [datasets_df]: [Dataframe of datasets read from data.Data(DATA_PREFIX)]
    :return: Unprocessed dataset
    :rtype: dataset.Unprocessed
    """
    if datasets_df.index.name != 'Dataset ID':
        datasets_df = datasets_df.set_index('Dataset ID')
    links = datasets_df.loc[unprocessed_source_id,'Download links']
    loader = datasets_df.loc[unprocessed_source_id,'Loader']
    loader_lib = ".".join(loader.split(".")[:-1])
    cls_str = loader.split(".")[-1]
    load_lib = importlib.import_module(f"pyrplib.{loader_lib}")
    cls = getattr(load_lib, cls_str)
    unprocessed = cls(unprocessed_source_id,links).load()
    return unprocessed

class Unprocessed(ABC):
    """
    Unprocessed dataset labeled with a persistant and unique dataset_id 
    """
    def __init__(self,dataset_id,links):
        self.dataset_id = dataset_id
        self.links = links
        self._data = None
        
    @abstractmethod
    def load(self,options={}):
        """
        Code that loads the data from the links
        """
        pass
    
    def data(self):
        """
        Returns a dataframe
        """
        assert type(self._data) == pd.DataFrame
        return self._data
    
    @abstractmethod
    def view(self):
        """
        Returns the visualizations for this dataset
        """
        pass
    
    @abstractmethod
    def type(self):
        """
        Return the high level type of an element in data() as a string
        """
        pass

    @abstractmethod
    def dash_ready_data(self):
        """
        Returns dash ready data
        """
        pass
    
    def view(self):
        """
        Standard view function for a dataset
        """
        data = self.dash_ready_data()
        if len(data) == 1:
            html_comps = []
            for j in range(len(data.columns)):
                d = data.iloc[0,j]
                html_comps.append(html.H3(data.columns[j]))
                if type(d) == pd.DataFrame:
                    html_comps.append(style.get_standard_data_table(d,f"data_view_{j}"))
                elif type(d) == list:
                    html_comps.append(html.Pre("\n".join(d)))
                else:
                    html_comps.append(html.Pre(d))
            return html_comps
        else:
            return [style.get_standard_data_table(data.reset_index(),"data_view")]
    
    def view_item(self,index):
        """
        Standard view function for an item from a dataset
        """
        data = self.dash_ready_data()
        item = data.loc[index]
        return style.view_item(item,"item_view")
    
class Processed(Unprocessed):
    """
    Processed dataset labeled with a persistant and unique dataset_id 
    """
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
    
    def dash_ready_data(self):
        return self.data

class ProcessedD(Processed):
    """
    Processed dominance (D) dataset object
    """
    def __init__(self):
        self._instance = pd.Series([None,None,None,None,None,None],
                                   index=["data","type","short_type","source_dataset_id","dataset_id","command"])
        
    def load(self,options={}):
        """
        Load a processed dominance (D) dataset with options
        """
        if type(self._instance['data']) != pd.DataFrame:
            data = pd.DataFrame(self._instance['data']).T # JSON load requires the transpose
            if "D" in data.index:
                self._instance['data'] = pd.DataFrame(data.loc['D','0'])
            else:
                self._instance['data'] = data
        return self
        
    @staticmethod
    def from_json(file):
        """Loads a ProcessedD file from a JSON file.

        :param [file]: [Path to local or http JSON file]
        :return: Returns a ProcessedD object.
        :rtype: ProcessedD
        """
        try:
            contents = json.loads(open(file).read())
        except:
            link = file # Try to see if this is a link instead of a file
            contents = requests.get(link).json()
        obj = ProcessedD()
        obj._instance = pd.Series(contents)
        return obj
    
    def size_str(self):
        """Size of dataset as a string
        """
        return ",".join([str(i) for i in self.data.shape])
    
    
class ProcessedGames(Processed):
    """
    Processed games dataset object
    """
    def __init__(self):
        self._instance = pd.Series([None,None,None,None,None,None],
                                   index=["data","type","short_type","source_dataset_id","dataset_id","command"])
        
    def load(self,options={}):
        """
        Load a processed games dataset with options
        """
        if type(self._instance['data']) == list: # first load from JSON
            games,teams = self._instance['data']
            if type(games) != pd.DataFrame:
                self._instance['data'] = (pd.DataFrame(games).T,teams)
            if type(teams) != list:
                self._instance['data'] = (games,list(teams))
        
        return self
    
    def size_str(self):
        """Size of dataset as a string
        """
        return "("+",".join([str(i) for i in self.data[0].shape])+"),"+str(len(self.data[1]))
        
    @staticmethod
    def from_json(file):
        """Loads a ProcessedGames file from a JSON file.

        :param [file]: [Path to local or http JSON file]
        :return: Returns a ProcessedGames object.
        :rtype: ProcessedGames
        """
        try:
            contents = json.loads(open(file).read())
        except:
            link = file # Try to see if this is a link instead of a file
            contents = requests.get(link).json()
        obj = ProcessedGames()
        obj._instance = pd.Series(contents)
        return obj
  