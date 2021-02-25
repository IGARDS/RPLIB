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
    return Ds
"""

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

"""
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
"""


class ProcessTransformer( BaseEstimator, TransformerMixin ):
    def __init__(self, index_cols, best_df, best_df_all, target_range, teams, all_teams):
        self.index_cols = index_cols
        self.best_df_all = best_df_all #
        self.target_range = target_range #
        self.teams = teams 
        self.all_teams = all_teams #
                 
    def fit( self, X, y = None ):
        return self
    
    def transform(self, problem, y = None ):
        # get variables we need from problem
        years = list(problem['data'].keys())
        days_to_subtract_keys = list(problem['data'][years[0]].keys())
        best_df = problem['other']['best_df']
        target_teams = problem['other'][self.teams]
        
        Ds = pd.DataFrame(columns=["D"]+self.index_cols)
        Ds.set_index(index_cols,inplace=True)
        for days_to_subtract_key,year in tqdm(itertools.product(days_to_subtract_keys,years)):
            days_to_subtract = float(days_to_subtract_key.split("=")[1])
            best_df = best_df_all.set_index('days_to_subtract').loc[days_to_subtract]
            for index,row in best_df.iterrows():
                dom,ran,dt,st,iw,method = row.loc['domain'],row.loc['range'],row.loc['direct_thres'],row.loc['spread_thres'],row.loc['weight_indirect'],row.loc['Method']
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


# problem: these can't be chained together currently...
# although i suppose the output doesn't need to be a df for intermediate steps?

"""
best_pred_df = best_pred_df.reset_index()
best_pred_df['days_to_subtract_key'] = "days_to_subtract="+best_pred_df['days_to_subtract'].astype(str)
best_pred_df
"""


class KeyColumnTransformer( BaseEstimator, TransformerMixin ):
    def __init__(self, col):
        self.col = col
        
    def fit( self, X, y = None ):
        return self
    
    def transform(self, df, y = None ):
        df = df.reset_index()
        df[col+'_key'] = col+df['col'].astype(str)
        return df


"""
feature_columns = ["delta_lop","delta_hillside","nfrac_xstar_lop","nfrac_xstar_hillside","diameter_lop","diameter_hillside"]

def compute_features(D,rankings,top_k):
    top_teams = list(rankings.sort_values().index[:top_k])
    D = D.loc[top_teams,top_teams]
    delta_lop,details_lop = pyrankability.rank.solve(D.fillna(0),method='lop',cont=True)

    x = pd.DataFrame(details_lop['x'],index=D.index,columns=D.columns)
    r = x.sum(axis=0)
    order = np.argsort(r)
    xstar = x.iloc[order,:].iloc[:,order]
    xstar.loc[:,:] = pyrankability.common.threshold_x(xstar.values)
    inxs = np.triu_indices(len(xstar),k=1)
    xstar_upper = xstar.values[inxs[0],inxs[1]]
    nfrac_upper_lop = sum((xstar_upper > 0) & (xstar_upper < 1))
    
    top_teams = xstar.columns[:top_k]
    
    k_two_distant,details_two_distant = pyrankability.search.solve_pair_max_tau(D.fillna(0),method='lop',cont=False,verbose=False)
    d_lop = details_two_distant['tau']
    
    delta_hillside,details_hillside = pyrankability.rank.solve(D,method='hillside',cont=True)
    
    x = pd.DataFrame(details_hillside['x'],index=D.index,columns=D.columns)
    r = x.sum(axis=0)
    order = np.argsort(r)
    xstar = x.iloc[order,:].iloc[:,order]
    xstar.loc[:,:] = pyrankability.common.threshold_x(xstar.values)
    inxs = np.triu_indices(len(xstar),k=1)
    xstar_upper = xstar.values[inxs[0],inxs[1]]
    nfrac_upper_hillside = sum((xstar_upper > 0) & (xstar_upper < 1))
    
    top_teams = xstar.columns[:top_k]
    
    k_two_distant,details_two_distant = pyrankability.search.solve_pair_max_tau(D,method='hillside',verbose=False,cont=False)
    d_hillside = details_two_distant['tau']
    
    features = pd.Series([delta_lop,delta_hillside,2*nfrac_upper_lop,2*nfrac_upper_hillside,d_lop,d_hillside],index=feature_columns)

    return features
"""


class ComputeFeaturesTransformer( BaseEstimator, TransformerMixin ):
    def __init__(self, rankings, top_k, feature_columns):
        self.rankings = rankings
        self.top_k = top_k
        self.feature_columns = feature_columns
        
    def fit( self, X, y = None ):
        return self
    
    def transform(self, D, y = None ):
        top_teams = list(rankings.sort_values().index[:top_k])
        D = D.loc[top_teams,top_teams]
        delta_lop,details_lop = pyrankability.rank.solve(D.fillna(0),method='lop',cont=True)

        x = pd.DataFrame(details_lop['x'],index=D.index,columns=D.columns)
        r = x.sum(axis=0)
        order = np.argsort(r)
        xstar = x.iloc[order,:].iloc[:,order]
        xstar.loc[:,:] = pyrankability.common.threshold_x(xstar.values)
        inxs = np.triu_indices(len(xstar),k=1)
        xstar_upper = xstar.values[inxs[0],inxs[1]]
        nfrac_upper_lop = sum((xstar_upper > 0) & (xstar_upper < 1))

        top_teams = xstar.columns[:top_k]

        k_two_distant,details_two_distant = pyrankability.search.solve_pair_max_tau(D.fillna(0),method='lop',cont=False,verbose=False)
        d_lop = details_two_distant['tau']

        delta_hillside,details_hillside = pyrankability.rank.solve(D,method='hillside',cont=True)

        x = pd.DataFrame(details_hillside['x'],index=D.index,columns=D.columns)
        r = x.sum(axis=0)
        order = np.argsort(r)
        xstar = x.iloc[order,:].iloc[:,order]
        xstar.loc[:,:] = pyrankability.common.threshold_x(xstar.values)
        inxs = np.triu_indices(len(xstar),k=1)
        xstar_upper = xstar.values[inxs[0],inxs[1]]
        nfrac_upper_hillside = sum((xstar_upper > 0) & (xstar_upper < 1))

        top_teams = xstar.columns[:top_k]

        k_two_distant,details_two_distant = pyrankability.search.solve_pair_max_tau(D,method='hillside',verbose=False,cont=False)
        d_hillside = details_two_distant['tau']

        features = pd.Series([delta_lop,delta_hillside,2*nfrac_upper_lop,2*nfrac_upper_hillside,d_lop,d_hillside],index=feature_columns)

        return features


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


