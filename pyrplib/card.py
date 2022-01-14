# Base Functionality for Reading and Processing
import os
import json
import requests
from abc import ABC, abstractmethod
import io

import base64
from io import BytesIO

import pandas as pd
import numpy as np

import dash_html_components as html

import pyrankability
import pyrplib

class Card(ABC):        
    def __init__(self):
        self._instance = pd.Series(index=["dataset_id","source_dataset_id","options"])
        
    def to_json(self):
        return self._instance.to_json(orient='columns')

    @staticmethod
    def get_contents(file):
        try:
            contents = json.loads(open(file).read())
        except:
            link = file # Try to see if this is a link instead of a file
            contents = requests.get(link).json()
        return pd.Series(contents)
        
    @property
    def source_dataset_id(self):
        return self._instance['source_dataset_id']
        
    @property
    def dataset_id(self):
        return self._instance['dataset_id']

    def load(self,dataset_id,options):
        self._instance['dataset_id'] = dataset_id
        self._instance['options'] = options
        return self
        
    @abstractmethod
    def prepare(self,processed_dataset):
        pass
    
    @abstractmethod
    def run(self):
        pass
    
    @abstractmethod
    def view(self):
        pass

class LOP(Card):
    def __init__(self):
        self._instance = pd.Series([set(),None,None,None,None,None,None,None,None],
                                   index=["solutions","obj","max_tau_solutions",
                                          "centroid_x","outlier_solution","dataset_id","source_dataset_id","options","D"])
    
    def prepare(self,processed_dataset):
        self._instance['source_dataset_id'] = processed_dataset['Source Dataset ID']
        d = pyrplib.dataset.ProcessedD.from_json(processed_dataset['Link']).load(processed_dataset['Options'])

        D = d.data.fillna(0)
    
        # Remove anything that has no information
        sums1 = D.sum(axis=0)
        sums2 = D.sum(axis=1)
        mask = sums1 + sums2 != 2*np.diag(D)
        D = D.loc[mask,mask]
        self._instance['D'] = D
        
    def run(self):
        assert 'source_dataset_id' in self._instance.index
        
        D = self.D
        # Solve using LP which is faster
        delta_lp,details_lp = pyrankability.rank.solve(D,method='lop',cont=True)

        # Next threshold numbers close to 1.0 or 0.0 and then convert to a dictionary style that is passed to later functions
        orig_sol_x = pyrankability.common.threshold_x(details_lp['x'])
        centroid_x = orig_sol_x
        self.centroid_x = centroid_x
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
        orig_sol_x = details['x']
        orig_obj = details['obj']
        first_solution = details['P'][0]

        # Add what we have found to our instance
        self.obj = orig_obj
        self.add_solution(first_solution)

        # Now we will see if there are multiple optimal solutions
        try:
            cont = False
            other_delta,other_detail = pyrankability.search.solve_any_diff(D,orig_obj,orig_sol_x,method='lop')
            other_solution = other_detail['perm']
            #print(other_solution['details']['P'])
            self.add_solution(other_solution)
            print('Found multiple solutions')
        except:
            print('Cannot find multiple solutions (or another problem occured)')

        if len(self.solutions) > 1: # Multiple optimal
            #solve_pair(D,D2=None,method=["lop","hillside"][1],minimize=False,min_ndis=None,max_ndis=None,tau_range=None,lazy=False,verbose=False)
            outlier_deltas,outlier_details = pyrankability.search.solve_fixed_cont_x(D,delta,centroid_x,method='lop',minimize=False)
            self.add_solution(outlier_details['perm'])
            self.outlier_solution = outlier_details['perm']

            centroid_deltas,centroid_details = pyrankability.search.solve_fixed_cont_x(D,delta,centroid_x,method='lop',minimize=True)
            self.add_solution(centroid_details['perm'])
            self.centroid_solution = centroid_details['perm']
               
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
    def from_json(file_link):
        contents = super(LOP, LOP).get_contents(file_link)
        obj = LOP()
        obj._instance = contents
        obj.load(contents['dataset_id'],contents['options'])
        obj._instance['D'] = pd.DataFrame(obj._instance['D'])
        obj._instance['centroid_x'] = np.array(obj._instance['centroid_x'])
        return obj
    
    def view(self):
        D = self.D
        centroid_x = pd.DataFrame(self.centroid_x,index=D.index,columns=self.D.columns)
        r = centroid_x.sum(axis=0).sort_values(ascending=False)
        contents = [html.H2("D(r,r)"),pyrplib.style.get_standard_data_table(self.D.loc[r.index,:].loc[:,r.index].reset_index(),"D_r_r")]
        
        # 'Red/Green plot':
        contents.append(html.H2("Red/Green plot"))
        xstar_g,scores,ordered_xstar=pyrankability.plot.show_single_xstar(centroid_x)
        plot_html = io.StringIO()
        xstar_g.save(plot_html, 'html')

        contents.append(html.Iframe(
            id='xstar_plot',
            height='500',
            width='1000',
            sandbox='allow-scripts',
            srcDoc=plot_html.getvalue(),
            style={'border-width': '0px'}
        ))
        
        # 'Nearest/Farthest Centoid Plot':
        contents.append(html.H2("Nearest/Farthest Centroid Plot"))
        outlier_solution = pd.Series(self.outlier_solution,
                                        index=D.index[self.outlier_solution],
                                        name="Farthest from Centroid")
        centroid_solution = pd.Series(self.centroid_solution,
                                        index=D.index[self.centroid_solution],
                                        name="Closest to Centroid")
        
        tmpfile = BytesIO()        
        pyrankability.plot.spider3(outlier_solution,centroid_solution,file=tmpfile)
        encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
        image_html = '<img src=\'data:image/png;base64,{}\'>'.format(encoded)

        contents.append(html.Iframe(
            id='nearest_farthest',
            height='500',
            width='1000',
            sandbox='allow-scripts',
            srcDoc=image_html,
            style={'border-width': '0px'}
        ))
                
        return contents

class Hillside(LOP):
    pass
