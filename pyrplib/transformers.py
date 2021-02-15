import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

import pyrankability

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
        ...
        
    #Return self nothing else to do here
    def fit( self, X, y = None  ):
        return self
    
    def transform(self, games , y = None ):
        games = games[[self.team1_name_col,self.team1_score_col,self.team2_name_col,self.team2_score_col]]
        map_func = lambda linked: pyrankability.construct.support_map_vectorized_direct_indirect(linked,direct_thres=self.direct_thres,spread_thres=self.spread_thres)
        Ddirect,Dindirect = pyrankability.construct.V_count_vectorized(games,map_func)
        return Ddirect,Dindirect
    
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