import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from tqdm import tqdm

# +
import sys
from pathlib import Path
home = str(Path.home())

sys.path.insert(0,"%s/rankability_toolbox_dev"%home)
sys.path.insert(0,"%s/RPLib"%home)
import pyrankability
# -

"""
        game_df = pd.DataFrame({"team1_name":games[year]['team1_name'],
                                "team1_score":games[year]['points1'],
                                "team2_name":games[year]['team2_name'],
                                "team2_score":games[year]['points2'],
                                "date": games[year]['date']
                               }).sort_values(by='date')
                               """

"""
def compute_D(game_df,team_range,direct_thres,spread_thres):
    map_func = lambda linked: pyrankability.construct.support_map_vectorized_direct_indirect(linked,direct_thres=direct_thres,spread_thres=spread_thres)
    Ds = pyrankability.construct.V_count_vectorized(game_df,map_func)
    for i in range(len(Ds)):
        Ds[i] = Ds[i].reindex(index=team_range,columns=team_range)
    return Ds"""

class IndividualGamesCountTransformer( BaseEstimator, TransformerMixin ):
    def __init__(self, team1_name_col = 'team1_name', team1_score_col='team1_score',
                 team2_name_col='team2_name',team2_score_col='team2_score',
                 direct_thres = 0, spread_thres = 0, individual_thres=True
                ):
        self.team1_name_col = team1_name_col
        self.team1_score_col = team1_score_col
        self.team2_name_col = team2_name_col
        self.team2_score_col = team2_score_col
        self.direct_thres = direct_thres
        self.spread_thres = spread_thres
        self.individual_thres = individual_thres
        
    #Return self nothing else to do here
    def fit( self, X, y = None  ):
        return self
    
    def transform(self, games , y = None ):
        games = games[[self.team1_name_col,self.team1_score_col,self.team2_name_col,self.team2_score_col]]
        map_func = lambda linked: pyrankability.construct.support_map_vectorized_direct_indirect(linked,direct_thres=self.direct_thres,spread_thres=self.spread_thres)
        Ddirect,Dindirect = pyrankability.construct.V_count_vectorized(games,map_func)
        # why don't we reindex here?
        return Ddirect,Dindirect

# +

def process(data,target,best_df_all):
    index_cols = ["Year","days_to_subtract_key","direct_thres","spread_thres","weight_indirect","range","Method"]
    Ds = pd.DataFrame(columns=["D"]+index_cols)
    Ds.set_index(index_cols,inplace=True)
    for days_to_subtract_key,year in tqdm(itertools.product(days_to_subtract_keys,years)):
        days_to_subtract = float(days_to_subtract_key.split("=")[1])
        best_df = best_df_all.set_index('days_to_subtract').loc[days_to_subtract]
        for index,row in best_df.iterrows():
            dom,ran,dt,st,iw,method = row.loc['domain'],row.loc['range'],row.loc['direct_thres'],row.loc['spread_thres'],row.loc['weight_indirect'],row.loc['Method']
            iw = 1 # Set this so we get both direct and indirect D matrices
            # set the team_range
            team_range = None
            if ran == 'madness':
                team_range = madness_teams[year]
            elif ran == 'all':
                team_range = all_teams[year]
            else:
                raise Exception(f"range={ran} not supported")
            name = (year,days_to_subtract_key,dt,st,iw,ran,method)
            if iw == 0:
                st = np.Inf
            D = compute_D(data[year][days_to_subtract_key],team_range,dt,st)
            Ds = Ds.append(pd.Series([D],index=["D"],name=name)) 
    return Ds



# -

class ProcessTransformer( BaseEstimator, TransformerMixin ):
    def __init__(self, index_cols, days_to_subtract_keys, years, best_df, best_df_all, 
                 dom, ran, dt, st, iw, method, target_range, target_teams, all_teams):
        self.index_cols = index_cols
        self.days_to_subtract_keys = days_to_subtract_keys
        self.years = years
        self.best_df = best_df # should we just pass in the problem df and get these here?
        self.best_df_all = best_df_all #
        self.dom = dom
        self.ran = ran
        self.dt = dt
        self.st = st
        self.iw = iw
        self.method = method
        self.target_range = target_range #
        self.target_teams = target_teams #
        self.all_teams = all_teams #
                 
    def fit( self, X, y = None ):
        return self
    
    def transform(self, data, y = None ):
        Ds = pd.DataFrame(columns=["D"]+self.index_cols)
        Ds.set_index(index_cols,inplace=True)
        for days_to_subtract_key,year in tqdm(itertools.product(days_to_subtract_keys,years)):
            days_to_subtract = float(days_to_subtract_key.split("=")[1])
            best_df = best_df_all.set_index('days_to_subtract').loc[days_to_subtract]
            for index,row in best_df.iterrows():
                iw = 1 # Set this so we get both direct and indirect D matrices
                # set the team_range
                team_range = None
                if ran == target_range:
                    team_range = target_teams[year]
                elif ran == 'all':
                    team_range = all_teams[year]
                else:
                    raise Exception(f"range={ran} not supported")
                name = (year,days_to_subtract_key,dt,st,iw,ran,method)
                if iw == 0:
                    st = np.Inf
                D = compute_D(data[year][days_to_subtract_key],team_range,dt,st)
                Ds = Ds.append(pd.Series([D],index=["D"],name=name)) 
        return Ds # can we return like this?


class ColumnDirectionTransformer( BaseEstimator, TransformerMixin ):
    def __init__(self,direction_column):
        self.direction_column = direction_column
    
    def fit( self, X, y = None):
        correlations = X.corr().loc[self.direction_column]
        self.signs = np.sign(correlations)
        return self
    
    def transform(self, X , y = None ):
        X2 = X.copy()
        for col in self.signs.index:
            if self.signs.loc[col] == -1:
                X2[col] = -1*X2[col]
        return X2

class ColumnCountTransformer( BaseEstimator, TransformerMixin ):
    def __init__(self,columns):
        self.columns = columns
        
    #Return self nothing else to do here
    def fit( self, X, y = None  ):
        return self
    
    def transform(self, X , y = None ):
        D = pd.DataFrame(np.zeros((len(X),len(X))),columns=X.index.copy(),index=X.index.copy())
        D.index.name = D.index.name+"1"
        D.columns.name = D.columns.name+"2"
        for col in self.columns:
            sorted_col = X[col].sort_values()
            for i in range(len(sorted_col)):
                D.loc[sorted_col.index[i], sorted_col.index[i+1:]] += 1
        return D


