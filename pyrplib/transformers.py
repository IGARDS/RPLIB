import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from tqdm import tqdm
import itertools
from sklearn.pipeline import Pipeline

from pyrankability import utils
from pyrankability import construct

from . import dataset

def count(games,teams):
    """Returns a processed direct matchup dominance matrix, processed indirect matchup dominance matrix, and the transformer used.

    :param [games]: [DataFrame of games (matchups between items)]
    :type [games]: [pandas.DataFrame]
    :param [teams]: [list of teams/items]
    :type [teams]: [list]
    :return: Tuple of processed D from direct matchups, processed D from indirect matchups, and the transformer
    :rtype: tuple
    """
    trans = ComputeDTransformer()
    trans.fit(games)
    D,ID = trans.transform(games)
    D = D.reindex(index=teams,columns=teams)
    ID = ID.reindex(index=teams,columns=teams)
    processed_D = dataset.ProcessedD()
    processed_D.data = D
    processed_D.load()
    processed_D.type = "Direct Count-based D Matrix"
    processed_D.short_type = "D"
    
    processed_ID = dataset.ProcessedD()
    processed_ID.data = ID
    processed_ID.load()
    processed_ID.type = "Indirect Count-based D Matrix"
    processed_ID.short_type = "D"
    
    return processed_D,processed_ID,trans

def directplusindirect(D,ID,trans,indirect_weight=1.):
    """Returns a processed D object that is a combination of D and ID using the indirect weight.

    :return: Processed dominance matrix that is a weighted combination of D and ID
    :rtype: processed_D
    """
    processed_D = dataset.ProcessedD()
    processed_D.data = D.data.fillna(0)+indirect_weight*ID.data.fillna(0)
    processed_D.load()
    processed_D.type = "Count-based D Matrix"
    processed_D.short_type = "D"
    return processed_D
    
def direct(D,ID,trans):
    """Returns the direct matchup (D) matrix from the arguments.
    """
    return D

def indirect(D,ID,trans):
    """Returns the indirect matchup (ID) matrix from the arguments.
    """
    return ID

def process_D(D):
    """Returns a processed D object from a dominance matrix (pandas.DataFrame).
    """
    processed_D = dataset.ProcessedD()
    processed_D.data = D
    processed_D.load()
    processed_D.type = "D Matrix"
    processed_D.short_type = "D"
    return processed_D

def standardize_games_teams(games,teams,options={}):
    """
    Returns a standardized version of games and teams with the expected column names as a ProcessedGames object. 
    
    options["team1_name"] = column in your dataframe that has team 1 names
    options["team2_name"] = column in your dataframe that has team 2 names
    options["team1_score"] = column in your dataframe that has team 1 score
    options["team2_score"] = column in your dataframe that has team 2 score
    options["team1_H_A_N"] = column in your dataframe to specifies home = 1, away = -1, or neutral = 0 for team 1
    options["team2_H_A_N"] = column in your dataframe to specifies home = 1, away = -1, or neutral = 0 for team 2
    """
    standardized_games = pd.DataFrame({
        "team1_name":games[options['team1_name']],
        "team1_score":games[options['team1_score']],
        "team1_H_A_N":games[options['team1_H_A_N']],
        "team2_name":games[options['team2_name']],
        "team2_score":games[options['team2_score']],
        "team2_H_A_N":games[options['team2_H_A_N']]},index=games.index)
    
    standardized_teams = list(teams)
    
    processed_games = dataset.ProcessedGames()
    processed_games.data = standardized_games,standardized_teams
    processed_games.load()
    processed_games.type = "Standardized Games"
    processed_games.short_type = "Games"
    return processed_games
    
def features_to_D(df_features,options={}):
    """
    Convert a features matrix to a dominance matrix.
    
    options["columns"] = list of columns you would like to convert
    options["items"] = list of items you would like to use. Items must be in the index
    """
    columns = df_features.columns
    items = df_features.index
    if "columns" in options:
        columns = options["columns"]
    if "items" in options:
        items = options["items"]
        
    trans = ColumnCountTransformer(columns).fit(df_features.loc[items])
    D = trans.transform(df_features.loc[items])
    processed_D = dataset.ProcessedD()
    processed_D.data = D
    processed_D.load()
    processed_D.type = "Features to D Matrix"
    processed_D.short_type = "D"
    
    return processed_D

class ColumnCountTransformer( BaseEstimator, TransformerMixin ):
    """
    A class to convert a feature matrix to a dominance matrix in the standard sklearn transformer paradigm. 
    """
    
    def __init__(self,columns):
        self.columns = columns

    #Return self nothing else to do here
    def fit( self, X, y = None  ):
        return self
   
    def transform(self, X , y = None ):
        D = pd.DataFrame(np.zeros((len(X),len(X))),columns=X.index.copy(),index=X.index.copy())
        D.index.name = str(D.index.name)+"1"
        D.columns.name = str(D.columns.name)+"2"
        for col in self.columns:
            sorted_col = X[col].sort_values()
            for i in range(len(sorted_col)):
                D.loc[sorted_col.index[i], sorted_col.index[i+1:]] += 1
        return D

class ComputeDTransformer(BaseEstimator, TransformerMixin):
    """
    A class to convert games to a dominance matrix in the standard sklearn transformer paradigm. 
    """
    def __init__(self, direct_thres=0, spread_thres=0,team_range=None):
        self.team_range = team_range
        self.direct_thres = direct_thres
        self.spread_thres = spread_thres

    # Return self nothing else to do here
    def fit( self, X, y = None  ):
        return self
   
    # X might be the games dataframe
    def transform(self, X, y = None ):
        map_func = lambda linked: construct.support_map_vectorized_direct_indirect(linked, direct_thres=self.direct_thres, spread_thres=self.spread_thres)
        Ds = construct.V_count_vectorized(X, map_func)
        if self.team_range is not None:
            for i in range(len(Ds)):
                Ds[i] = Ds[i].reindex(index=self.team_range,columns=self.team_range)
        return Ds
