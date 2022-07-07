# Base Functionality for Reading and Processing
import os
import json
import requests
from abc import ABC, abstractmethod
import io
import copy

import base64
from io import BytesIO
from io import StringIO

import pandas as pd
import numpy as np

from dash import html

import pyrankability
import pyrplib

class Card(ABC):
    """
    The base Card abstract class. 
    """
    def __init__(self):
        self._instance = pd.Series(index=["dataset_id","source_dataset_id","options"])
        
    def to_json(self):
        """Returns a JSON string representing the object.

        :return: Returns a JSON string representing the object.
        :rtype: str
        """
        return self._instance.to_json(orient='columns')
    
    def load(self,dataset_id,options):
        """Load a Card using the dataset_id and the options.

        :param [dataset_id]: [Dataset ID]
        :param [options]: [Dictionary of options]
        :type [options]: [dict]
        """
        self._instance['dataset_id'] = dataset_id
        self._instance['options'] = options
        return self

    @staticmethod
    def get_contents(file):
        """Static method that reads a Card from a JSON file. 

        :param [file]: [file path or URL path to JSON file]
        :type [file]: [str]
        :return: Returns a Pandas Series object
        :rtype: pandas.Series
        """
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
    
    @property
    def options(self):
        return self._instance['options']
        
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
    """
    A class that represents the analysis, results, and metrics associated with running LOP algorithm. 
    
    LOP card can be saved as a JSON file that contains the following:
    
    .. code-block:: json
    
        {
            "dataset_id": "<Identifying Dataset ID>"
            "source_dataset_id": "<Identifying Source Dataset ID>"
            "D": "<Dominance matrix and input to the LOP solver>",
            "obj": "<Optimal value of LOP>",
            "solutions": "<List of optimal orderings/permutations that result in an optimal value>",
            "farthest_pair": "<Two farthest orderings/permutations measured by Kendall tau (when available)>",
            "tau_farthest_pair": "<Associated Kendall tau value (when available)>",
            "closest_pair": "<Two (not identical) closest orderings/permutations measured by Kendall tau (when available)>",
            "tau_closest_pair": "<Associated Kendall tau value (when available)>",
            "centroid_x": "<X*>",
            "outlier_solution": "<Optimal ordering/permutation that is farthest from centroid_x>",
            "method": "<Method which is LOP or Hillside>"
        }
    """
    def __init__(self):
        self._instance = pd.Series([set(),None,None,None,None,None,None,None,"lop",None,None,None,None],
                                   index=["solutions",
                                          "obj",
                                          "centroid_x",
                                          "outlier_solution",
                                          "dataset_id",
                                          "source_dataset_id",
                                          "options",
                                          "D",
                                          "method",
                                          "closest_pair",
                                          "farthest_pair",
                                          "tau_farthest_pair",
                                          "tau_closest_pair"
                                         ])
    
    
    def prepare(self,processed_dataset):
        """Prepare the data for analysis. For LOP this means filling in missing values in the dominance matrix
        and removing rows and columns with all 0's. 

        :param [processed_dataset]: [Processed dataset object]
        :type [processed_dataset]: [dataset.Processed]
        :return: self
        :rtype: LOP
        """
        if type(processed_dataset) == pyrplib.dataset.ProcessedD:
            d = copy.deepcopy(processed_dataset)
            self._instance['source_dataset_id'] = -1
        else:
            self._instance['source_dataset_id'] = processed_dataset.name #['Dataset ID']
            d = pyrplib.dataset.ProcessedD.from_json(processed_dataset['Link']).load(processed_dataset['Options'])

        D = d.data.fillna(0)
    
        # Remove anything that has no information
        sums1 = D.sum(axis=0)
        sums2 = D.sum(axis=1)
        mask = sums1 + sums2 != 2*np.diag(D)
        D = D.loc[mask,mask]
        self._instance['D'] = D
        return self
    
    @property
    def xstar(self):
        """Return X* as a dataframe using the row and column names of D.
        """
        Xstar = pd.DataFrame(pyrankability.common.threshold_x(self.centroid_x),index=self.D.index,columns=self.D.columns)
        return Xstar
    
    @property
    def xstar_r_r(self):
        """Return X* optimally reordered.
        """
        r = self.r #self.centroid_x.sum(axis=1).sort_values(ascending=False)
        Xstar = self.xstar
        Xstar_r_r = Xstar.loc[r.index,r.index]
        return Xstar_r_r

    def run(self):
        """Run the LOP analysis and compute the metrics.
        """
        assert 'source_dataset_id' in self._instance.index
        
        D = self.D
        # Solve using LP which is faster
        delta_lp,details_lp = pyrankability.rank.solve(D,method=self.method,cont=True)

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
        delta,details = pyrankability.rank.solve(D,method=self.method,fix_x=fix_x,cont=cont)
        orig_sol_x = details['x']
        orig_obj = details['obj']
        first_solution = details['P'][0]

        # Add what we have found to our instance
        self.obj = orig_obj
        self.add_solution(first_solution)
        
        # Now we will see if there are multiple optimal solutions
        try:
            cont = False
            other_delta,other_detail = pyrankability.search.solve_any_diff(D,orig_obj,orig_sol_x,method=self.method)
            other_solution = other_detail['perm']
            self.add_solution(other_solution)
            #print('Found multiple solutions')
        except:
            print('Cannot find multiple solutions (or another problem occured)')
            
        if len(self.solutions) > 1: # if multiple
            outlier_deltas,outlier_details = pyrankability.search.solve_fixed_cont_x(D,orig_obj,centroid_x,method=self.method,minimize=False)
            self.add_solution(outlier_details['perm'])
            self.outlier_solution = outlier_details['perm']

            centroid_deltas,centroid_details = pyrankability.search.solve_fixed_cont_x(D,orig_obj,centroid_x,method=self.method,minimize=True)
            self.add_solution(centroid_details['perm'])
            self.centroid_solution = centroid_details['perm']

            # Now get ready to run scip
            obj_lop_scip,details_lop_scip = pyrankability.rank.solve(D,method=self.method,include_model=True,cont=False)
            model = details_lop_scip['model']
            model_file = pyrankability.common.write_model(model)
            max_num_solutions = 1000
            if type(self.options) == dict and "max_num_solutions" in self.options:
                max_num_solutions = self.options['max_num_solutions']
            results = pyrankability.search.scip_collect(D,model_file,max_num_solutions=max_num_solutions,show_output=False)
            for sol in results['perms']:
                self.add_solution(sol)

            if len(self.solutions) > 1: # Multiple optimal available
                obj_lop_pair, details_lop_pair = pyrankability.search.solve_pair(D,method=self.method,minimize=False)
                perm_x = details_lop_pair['perm_x']
                perm_y = details_lop_pair['perm_y']
                self.add_solution(perm_x)
                self.add_solution(perm_y)
                self.farthest_pair = (perm_x,perm_y)
                self.tau_farthest_pair = pyrankability.common.tau(details_lop_pair['perm_x'],details_lop_pair['perm_y'])

                obj_lop_pair, details_lop_pair = pyrankability.search.solve_pair(D,method=self.method,minimize=True,min_ndis=1)
                perm_x = details_lop_pair['perm_x']
                perm_y = details_lop_pair['perm_y']
                self.add_solution(perm_x)
                self.add_solution(perm_y)
                self.closest_pair = (perm_x,perm_y)
                self.tau_closest_pair = pyrankability.common.tau(details_lop_pair['perm_x'],details_lop_pair['perm_y'])
        return self
                
    @property
    def method(self):
        return self._instance['method']
    
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
    def beta(self):    
        Xstar_r_r = self.xstar_r_r #Xstar.iloc[np.array(first_solution),np.array(first_solution)]
        return pyrankability.features.beta(Xstar_r_r,normalize=True,average=True)
        
    @property
    def farthest_pair(self):
        return self._instance['farthest_pair']
       
    @farthest_pair.setter
    def farthest_pair(self, farthest_pair):
        self._instance['farthest_pair'] = farthest_pair
        
    @property
    def closest_pair(self):
        return self._instance['closest_pair']
       
    @closest_pair.setter
    def closest_pair(self, closest_pair):
        self._instance['closest_pair'] = closest_pair
        
    @property
    def tau_closest_pair(self):
        return self._instance['tau_closest_pair']
       
    @tau_closest_pair.setter
    def tau_closest_pair(self, tau_closest_pair):
        self._instance['tau_closest_pair'] = tau_closest_pair    
        
    @property
    def tau_farthest_pair(self):
        return self._instance['tau_farthest_pair']
       
    @tau_farthest_pair.setter
    def tau_farthest_pair(self, tau_farthest_pair):
        self._instance['tau_farthest_pair'] = tau_farthest_pair  
        
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
        """Adds a solution specified by a permutation/ordering.

        :param [sol]: [A permutation/ordering of type list or tuple]
        """
        if type(sol) != tuple:
            sol = tuple(sol)
        self._instance['solutions'].add(sol)
        
    @staticmethod
    def from_json(file_link):
        """Static method that reads a LOP card object from a JSON file. 

        :return: Returns a LOP card object
        :rtype: LOP
        """
        contents = super(LOP, LOP).get_contents(file_link)
        if 'method' not in contents or contents['method'] == 'lop': # TODO: remove backward compatibility
            obj = LOP()
        elif contents['method'] == 'hillside':
            obj = Hillside()
        obj._instance = contents
        obj.load(contents['dataset_id'],contents['options'])
        obj._instance['D'] = pd.DataFrame(obj._instance['D'])
        obj._instance['centroid_x'] = np.array(obj._instance['centroid_x'])
        return obj
    
    def view(self):
        """Returns a dictionary in dash ready format. 

        :return: List of HTML dash ready objects
        :rtype: list
        """
        contents = []
        visuals = self.get_visuals()['dash']
        for key in visuals:
            contents.append(html.H2(key))
            contents.append(visuals[key])
            
        return contents
    
    @property
    def r(self):
        """Returns a rating vector using X*. 

        :return: Rating vector derived from X* 
        :rtype: pandas.Series
        """
        return self.xstar.sum(axis=1).sort_values(ascending=False)
    
    def get_visuals(self):
        """Returns a diciontary with both dash and notebook ready visualization. 

        :return: Dash and notebook visuals
        :rtype: dict
        """
        D = self.D
        visuals = {"notebook":{},"dash":{}}
                
        r = self.r
        visuals["dash"]["D[r,r]"] = pyrplib.style.get_standard_data_table(self.D.loc[r.index,:].loc[:,r.index].reset_index(),"D_r_r")
        visuals["notebook"]["D[r,r]"] = self.D.loc[r.index,:].loc[:,r.index]
        
        Xstar_r_r = self.xstar_r_r
        visuals["dash"]["X*[r,r]"] = pyrplib.style.get_standard_data_table(Xstar_r_r.reset_index(),"X_r_r")
        visuals["notebook"]["X*[r,r]"] = Xstar_r_r
        
        # 'Red/Green plot':
        xstar_width_height = len(Xstar_r_r) * 10
        xstar_g=pyrankability.plot.show_single_xstar(Xstar_r_r)#centroid_x)
        xstar_g = xstar_g.properties(
            width=xstar_width_height,
            height=xstar_width_height
        )
        visuals["notebook"]["X* (red/green)"] = xstar_g
        plot_html = io.StringIO()
        xstar_g.save(plot_html, 'html')

        visuals["dash"]["X* (red/green)"] = html.Iframe(
            id='xstar_plot',
            height=str(xstar_width_height + 150),
            width=str(xstar_width_height + 150),
            sandbox='allow-scripts',
            srcDoc=plot_html.getvalue(),
            style={'border-width': '0px'}
        )
        
        # 'X*':
        xstar_width_height = len(Xstar_r_r) * 10
        xstar_g=pyrankability.plot.show_single_xstar(Xstar_r_r,red_green=False)
        xstar_g = xstar_g.properties(
            width=xstar_width_height,
            height=xstar_width_height
        )
        visuals["notebook"]["X* (greyscale)"] = xstar_g
        plot_html = io.StringIO()
        xstar_g.save(plot_html, 'html')

        visuals["dash"]["X* (greyscale)"] = html.Iframe(
            id='xstar2_plot',
            height=str(xstar_width_height + 150),
            width=str(xstar_width_height + 150),
            sandbox='allow-scripts',
            srcDoc=plot_html.getvalue(),
            style={'border-width': '0px'}
        )
        
        if len(self.solutions) > 1:
            # nearest and farthest
            outlier_solution = pd.Series(self.outlier_solution,
                                            index=D.index[np.array(self.outlier_solution)].astype(str),
                                            name="Farthest from Centroid")
            centroid_solution = pd.Series(self.centroid_solution,
                                            index=D.index[np.array(self.centroid_solution)].astype(str),
                                            name="Closest to Centroid")

            spider_g = pyrankability.plot.spider(outlier_solution,centroid_solution)
            spider_width = 700
            spider_height = 30 * len(outlier_solution)
            spider_g = spider_g.properties(
                width = spider_width,
                height = spider_height
            ).interactive()

            visuals["notebook"]["Nearest and Farthest"] = spider_g

            tmpfile = StringIO()
            spider_g.save(tmpfile, 'html')   
            visuals["dash"]["Nearest and Farthest"] = html.Iframe(
                id='nearest_farthest',
                height=str(spider_height + 100),
                width=str(spider_width + 400),
                sandbox='allow-scripts',
                # Once this function returns, tmpfile is garbage collected and may be 
                # the reason for 'view source' not working. 
                # TODO: Look into the return of getvalue() and implications that has on 'srcDoc'
                srcDoc=tmpfile.getvalue(), 
                style={'border-width': '0px'}
            )

            # Farthest pair
            #farthest_pair
            first,second = self.farthest_pair
            first_solution = pd.Series(first,
                                            index=D.index[np.array(first)].astype(str),
                                            name="Solution 1")
            second_solution = pd.Series(second,
                                            index=D.index[np.array(second)].astype(str),
                                            name="Solution 2")

            spider_g = pyrankability.plot.spider(first_solution,second_solution)
            spider_width = 500
            spider_height = 30 * len(second)
            spider_g = spider_g.properties(
                width = spider_width,
                height = spider_height
            ).interactive()

            visuals["notebook"]["Farthest Pair"] = spider_g

            tmpfile = StringIO()
            spider_g.save(tmpfile, 'html')   
            visuals["dash"]["Farthest Pair"] = html.Iframe(
                id='farthest_pair',
                height=str(spider_height + 100),
                width=str(spider_width + 600),
                sandbox='allow-scripts',
                # Once this function returns, tmpfile is garbage collected and may be 
                # the reason for 'view source' not working. 
                # TODO: Look into the return of getvalue() and implications that has on 'srcDoc'
                srcDoc=tmpfile.getvalue(), 
                style={'border-width': '0px'}
            )
        
        
        visuals["notebook"]["OBJECTIVE"] = self.obj
        visuals["dash"]["OBJECTIVE"] = self.obj
        visuals["notebook"]["BETA"] = self.beta
        visuals["dash"]["BETA"] = self.beta
        if len(self.solutions) > 1:        
            visuals["notebook"]["TAU Farthest Pair"] = self.tau_farthest_pair
            visuals["notebook"]["TAU Closest Pair"] = self.tau_closest_pair
            visuals["dash"]["TAU Farthest Pair"] = self.tau_farthest_pair
            visuals["dash"]["TAU Closest Pair"] = self.tau_closest_pair
        visuals["notebook"]["Number of optimal solutions found"] = len(self.solutions)
        visuals["dash"]["Number of optimal solutions found"] = len(self.solutions)
        
        return visuals
        

class Hillside(LOP):
    """
    A class that represents the analysis, results, and metrics associated with running Hillside algorithm. 
    
    Hillside finds the optimal solution in Hillside form:
    
    Chartier, Timothy P., et al. "Minimum violations sports ranking using evolutionary optimization and binary integer linear program approaches." Proceedings of the Tenth Australian Conference on Mathematics and Computers in Sport, A. Bedford and M. Ovens, eds., MathSport (ANZIAM), New South Wales, Australia. 2010.
    
    Hillside and LOP share the same metrics and analysis.
    """
    def __init__(self):
        super().__init__()
        self._instance['method'] = 'hillside'

class SystemOfEquations(Card):
    """
    A class that represents the analysis, results, and metrics associated with solving a system of equations to produce a ranking. 
    
    SystemOfEquations card can be saved as a JSON file that contains the following:
    
    .. code-block:: json
    
        {
            "dataset_id": "<Identifying Dataset ID>"
            "source_dataset_id": "<Identifying Source Dataset ID>"
            "M": "<Matrix from Mx=b>",
            "b": "<Vector from Mx=b>",
            "r": "<Rating vector>",
            "ranking": "<Ranking vector>",
            "perm": "<Ordering/permutation>",
            "options": "<dictionary of options>",
            "games": "<Games (or more generally matchups) that are processed to produce M and b>",
            "teams": "<List of teams (or more generally items)>",
            "method": "<Method which is Massey or Colley>"
        }
    """
    def __init__(self,method):
        self._instance = pd.Series(index=["r","ranking","perm","dataset_id","source_dataset_id","options","games","teams","method","b","M"])
        self._instance['method'] = method
    
    def prepare(self,processed_dataset):
        """Prepare the data for analysis.

        :param [processed_dataset]: [Processed dataset object]
        :type [processed_dataset]: [dataset.Processed]
        :return: self
        :rtype: SystemOfEquations
        """
        self._instance['source_dataset_id'] = processed_dataset.name #['Dataset ID']
        d = pyrplib.dataset.ProcessedGames.from_json(processed_dataset['Link']).load(processed_dataset['Options'])

        self.games,self.teams = d.data
        
        if self.method == 'colley':
            map_func = lambda linked: pyrankability.construct.colley_matrices(linked)
        elif self.method == 'massey':
            map_func = lambda linked: pyrankability.construct.massey_matrices(linked)
        
        M,b,indirect_M,indirect_b = pyrankability.construct.map_vectorized(self.games,map_func)
        M = M.reindex(index=self.teams,columns=self.teams)
        b = b.reindex(self.teams)
        mask = b.isna()
        b = b.loc[~mask]
        M = M.loc[~mask,~mask]
        self.b = b
        self.M = M
        return self
        
    def run(self):
        """Solve the system of equations and store the results.
        """
        assert 'source_dataset_id' in self._instance.index
        
        #inxs = list(np.where(mask)[0])
        ranking,r,perm = pyrankability.rank.ranking_from_matrices(self.M.fillna(0),self.b)
        sorted_ixs = np.argsort(-r)
        self.ranking = ranking.iloc[sorted_ixs]
        self.r = r.iloc[sorted_ixs]
        self.perm = perm

    @property
    def method(self):
        return self._instance['method']
    
    @property
    def M(self):
        return self._instance['M']
       
    @M.setter
    def M(self, M):
        self._instance['M'] = M
        
    @property
    def b(self):
        return self._instance['b']
       
    @b.setter
    def b(self, b):
        self._instance['b'] = b
        
    @property
    def games(self):
        return self._instance['games']
       
    @games.setter
    def games(self, games):
        self._instance['games'] = games
        
    @property
    def teams(self):
        return self._instance['teams']
       
    @teams.setter
    def teams(self, teams):
        self._instance['teams'] = teams
        
    @property
    def r(self):
        return self._instance['r']
       
    @r.setter
    def r(self, r):
        self._instance['r'] = r    
        
    @property
    def ranking(self):
        return self._instance['ranking']
       
    @ranking.setter
    def ranking(self, ranking):
        self._instance['ranking'] = ranking
        
    @property
    def perm(self):
        return self._instance['perm']
       
    @perm.setter
    def perm(self, perm):
        self._instance['perm'] = perm   
        
    @staticmethod
    def from_json(file_link):
        """Static method that reads a SystemOfEquations card object from a JSON file. 

        :return: Returns a SystemOfEquations card object
        :rtype: SystemOfEquations
        """
        contents = super(SystemOfEquations, SystemOfEquations).get_contents(file_link)
        obj = SystemOfEquations(contents['method'])
        obj._instance = contents
        obj.load(contents['dataset_id'],contents['options'])
        obj._instance['games'] = pd.DataFrame(obj._instance['games'])
        obj._instance['r'] = pd.Series(obj._instance['r'])
        obj._instance['ranking'] = pd.Series(obj._instance['ranking'])
        obj._instance['perm'] = pd.Series(obj._instance['perm'])
        obj._instance['M'] = pd.DataFrame(obj._instance['M'])
        obj._instance['b'] = pd.Series(obj._instance['b'])
        return obj
    
    def view(self):
        """Returns a dictionary in dash ready format. 

        :return: List of HTML dash ready objects
        :rtype: list
        """
        games = self.games
        M = self.M
        b = self.b
        contents = [html.H2("M"),pyrplib.style.get_standard_data_table(M,"M")]
        contents.extend([html.H2("b"),pyrplib.style.get_standard_data_table(b,"b")])
        contents.extend([html.H2("r"),pyrplib.style.get_standard_data_table(self.r,"r")])
        contents.extend([html.H2("Ranking"),pyrplib.style.get_standard_data_table(self.ranking,"ranking")])
        contents.extend([html.H2("Perm"),pyrplib.style.get_standard_data_table(self.perm,"perm")])
                
        return contents