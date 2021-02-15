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