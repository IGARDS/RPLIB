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
    processed_D = dataset.ProcessedD()
    processed_D.data = D.data.fillna(0)+indirect_weight*ID.data.fillna(0)
    processed_D.load()
    processed_D.type = "Count-based D Matrix"
    processed_D.short_type = "D"
    return processed_D
    
def direct(D,ID,trans):
    return D

def indirect(D,ID,trans):
    return ID

def process_D(D):
    processed_D = dataset.ProcessedD()
    processed_D.data = D
    processed_D.load()
    processed_D.type = "D Matrix"
    processed_D.short_type = "D"
    return processed_D

def standardize_games_teams(games,teams,options={}):
    """
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
    
    return standardized_games,standardized_teams

def features_to_D(df_features,options={}):
    """
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
