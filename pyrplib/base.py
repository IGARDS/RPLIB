# Base Functionality for Reading and Processing
import os
import json
import requests

import pandas as pd

class MatricesInfo:
    """
    A class to represent information about matrices M and b. i.e., MX=b
    """
    def __init__(self):
        """
        Constructs all the necessary attributes for the object.
        """
        self._instance = pd.Series([None,None,None,None,None],
                                   index=["matrix","b","source_dataset_id","dataset_id","command"])
        
    def to_json(self):
        """Returns a JSON string representing the object.

        :return: Returns a JSON string representing the object.
        :rtype: str
        """
        return self._instance.to_json()
    
    @staticmethod
    def from_json(file):
        """Static method that reads a MatricesInfo object from a JSON file. 

        :return: Returns a MatricesInfo object
        :rtype: MatricesInfo
        """
        try:
            contents = json.loads(open(file).read())
        except:
            link = file # Try to see if this is a link instead of a file
            contents = requests.get(link).json()
        obj = MatricesInfo()
        obj._instance = pd.Series(contents)
        return obj
       
    @property
    def matrix(self):
        return self._instance['matrix']
       
    @matrix.setter
    def matrix(self, matrix):
        self._instance['matrix'] = matrix
        
    @property
    def b(self):
        return self._instance['b']
       
    @b.setter
    def b(self, b):
        self._instance['b'] = b
        
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

class DInfo:
    """
    A class to represent information about a dominance (D) matrix.
    """
    def __init__(self):
        self._instance = pd.Series([None,None,set(),None,None],
                                   index=["D","D_type","source_dataset_id","dataset_id","command"])
        
    def to_json(self):
        """Returns a JSON string representing the object.

        :return: Returns a JSON string representing the object.
        :rtype: str
        """
        return self._instance.to_json()
    
    @staticmethod
    def from_json(file):
        """Static method that reads a DInfo object from a JSON file. 

        :return: Returns a DInfo object
        :rtype: DInfo
        """
        try:
            contents = json.loads(open(file).read())
        except:
            link = file # Try to see if this is a link instead of a file
            contents = requests.get(link).json()
        obj = DInfo()
        obj._instance = pd.Series(contents)
        return obj
       
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
    """
    A class that represents the analysis, results, and metrics associated with running LOP algorithm. 
    
    LOPCard can be saved as a JSON file that contains the following:
    
    .. code-block:: json
    
        {
            "D": "<Dominance matrix and input to the LOP solver>",
            "obj": "<Optimal value of LOP>",
            "solutions": "<List of optimal orderings/permutations that result in an optimal value>",
            "max_tau_solutions": "<Two farthest orderings/permutations measured by Kendall tau (when available)>",
            "centroid_x": "<X*>",
            "outlier_solution": "<Optimal ordering/permutation that is farthest from centroid_x>",
            "dataset_id": "<Identifying ID>"
        }
    """
    def __init__(self):
        self._instance = pd.Series([None,None,set(),None,None,None,None],
                                   index=["D","obj","solutions","max_tau_solutions",
                                          "centroid_x","outlier_solution","dataset_id"])
            
    def to_json(self,file):
        """Returns a JSON string representing the object.

        :return: Returns a JSON string representing the object.
        :rtype: str
        """
        self._instance.to_json(file,orient='columns')
        
    def add_solution(self,sol):
        """Adds a solution specified by a permutation/ordering.

        :param [sol]: [A permutation/ordering of type list or tuple]
        """
        if type(sol) != tuple:
            sol = tuple(sol)
        self._instance['solutions'].add(sol)
        
    @staticmethod
    def from_json(file):
        """Static method that reads a LOPCard object from a JSON file. 

        :return: Returns a LOPCard object
        :rtype: LOPCard
        """
        try:
            contents = json.loads(open(file).read())
        except:
            link = file # Try to see if this is a link instead of a file
            contents = requests.get(link).json()
        obj = LOPCard()
        obj._instance = pd.Series(contents)
        return obj
       
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
                            
class HillsideCard(LOPCard):
    pass

