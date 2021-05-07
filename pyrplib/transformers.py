import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from tqdm import tqdm
import itertools
from sklearn.pipeline import Pipeline

# +
import sys
from pathlib import Path
home = str(Path.home())

#sys.path.insert(0,"%s/rankability_toolbox_dev"%home)
#sys.path.insert(0,"%s/RPLib"%home)
import pyrankability
import pyrplib
# -

# ### Baseline 0001

# **Function to compute a D matrix from games using hyperparameters**

"""
def compute_D(game_df,team_range,direct_thres,spread_thres):
    map_func = lambda linked: pyrankability.construct.support_map_vectorized_direct_indirect(linked,direct_thres=direct_thres,spread_thres=spread_thres)
    Ds = pyrankability.construct.V_count_vectorized(game_df,map_func)
    for i in range(len(Ds)):
        Ds[i] = Ds[i].reindex(index=team_range,columns=team_range)
    return Ds
"""


class ComputeDTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, direct_thres, spread_thres,team_range=None):
        self.team_range = team_range
        self.direct_thres = direct_thres
        self.spread_thres = spread_thres
        
    # Return self nothing else to do here
    def fit( self, X, y = None  ):
        return self
    
    # X might be the games dataframe
    def transform(self, X, y = None ):
        map_func = lambda linked: pyrankability.construct.support_map_vectorized_direct_indirect(linked, direct_thres=self.direct_thres, spread_thres=self.spread_thres)
        Ds = pyrankability.construct.V_count_vectorized(X, map_func)
        if self.team_range is not None:
            for i in range(len(Ds)):
                Ds[i] = Ds[i].reindex(index=self.team_range,columns=self.team_range)
        return Ds


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
            iw = .1 # Set this so we get both direct and indirect D matrices
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
            compute_pipe = Pipeline([('compute_D', pyrplib.transformers.ComputeDTransformer(team_range, dt, st))])
            X = data[year][days_to_subtract_key]
            pipe.fit(X)
            D = pipe.transform(X)
            #D = compute_D(data[year][days_to_subtract_key],team_range,dt,st)
            Ds = Ds.append(pd.Series([D],index=["D"],name=name)) 
    return Ds
"""


class ProcessTransformer(BaseEstimator, TransformerMixin):
    # where team_ran is a column like 'madness' and ran_teams is a df like 'madness_teams'
    def __init__(self, index_cols, days_to_subtract_keys, years, team_ran, ran_teams, best_df_all):
        self.index_cols = index_cols
        self.days_to_subtract_keys = days_to_subtract_keys
        self.years = years
        self.team_ran = team_ran
        self.ran_teams = ran_teams
        self.best_df_all = best_df_all
        
    # Return self nothing else to do here
    def fit( self, X, y = None  ):
        return self
    
    # X might be the games dataframe
    def transform(self, X, y = None ):
        Ds = pd.DataFrame(columns=["D"]+self.index_cols)
        Ds.set_index(self.index_cols,inplace=True)
        for days_to_subtract_key,year in tqdm(itertools.product(self.days_to_subtract_keys,self.years)):
            days_to_subtract = float(days_to_subtract_key.split("=")[1])
            best_df = self.best_df_all.set_index('days_to_subtract').loc[days_to_subtract]
            for index,row in best_df.iterrows():
                dom,ran,dt,st,iw,method = row.loc['domain'],row.loc['range'],row.loc['direct_thres'],row.loc['spread_thres'],row.loc['weight_indirect'],row.loc['Method']
                iw = .1 # Set this so we get both direct and indirect D matrices
                # set the team_range
                team_range = None
                if ran == self.team_ran:
                    team_range = self.ran_teams[year]
                else:
                    raise Exception(f"range={ran} not supported")
                name = (year,days_to_subtract_key,dt,st,iw,ran,method)
                if iw == 0:
                    st = np.Inf
                pipe = Pipeline([('compute_D', pyrplib.transformers.ComputeDTransformer(team_range, dt, st))])
                X_year = X[year][days_to_subtract_key]
                pipe.fit(X_year)
                D = pipe.transform(X_year)
                Ds = Ds.append(pd.Series([D],index=["D"],name=name)) 
        return Ds


"""
def create_features(Ds,rankings_df,top_k):
    index_cols = list(Ds.index.names)+["Construction"]
    X = pd.DataFrame(columns=index_cols + feature_columns)
    X.set_index(index_cols,inplace=True)
    #target = target.set_index(['days_to_subtract2','Year','direct_thres','spread_thres','weight_indirect','range','Method'])
    for index,row in tqdm(Ds.iterrows()):
        sum_D = None
        year,days_to_subtract_key,dt,st,iw,ran,method = index
        days_to_subtract = int(days_to_subtract_key.split("=")[1])
        print(days_to_subtract,year,dt,st,iw,ran,method)
        rankings = rankings_df.loc[days_to_subtract,year,dt,st,iw,ran,method].dropna() #spec_best_pred_df = best_pred_df.set_index(['Year','days_to_subtract_key',"Method"]).loc[[(year,days_to_subtract_key,method)]]
        for i,D in enumerate(Ds.loc[(year,days_to_subtract_key,dt,st,iw,ran,method),"D"]):
            if sum_D is None:
                sum_D = D
            else:
                sum_D = sum_D.add(iw*D,fill_value=0)
            if i == 0:
                construction = "Direct"
            elif i == 1:
                construction = "Indirect"
            else:
                raise Exception("Error")
            features = pyrplib.utils.compute_features(D,rankings,top_k,feature_columns)
            features.name = tuple(list(index)+[construction])
            X = X.append(features)
            
            if i == 1:
                construction = "Both"
                features = pyrplib.utils.compute_features(sum_D,rankings,top_k,feature_columns)
                features.name = tuple(list(index)+[construction])
                X = X.append(features)
    return X
"""


class CreateFeaturesTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, feature_columns, rankings_df, top_k):
        self.feature_columns = feature_columns
        self.rankings_df = rankings_df
        self.top_k = top_k
        
    # Return self nothing else to do here
    def fit( self, X, y = None  ):
        return self
    
    # X might be the games dataframe
    def transform(self, X, y = None ):
        index_cols = list(X.index.names)+["Construction"]
        X_new = pd.DataFrame(columns=index_cols + self.feature_columns)
        X_new.set_index(index_cols,inplace=True)
        #target = target.set_index(['days_to_subtract2','Year','direct_thres','spread_thres','weight_indirect','range','Method'])
        for index,row in tqdm(X.iterrows()):
            sum_D = None
            year,days_to_subtract_key,dt,st,iw,ran,method = index
            days_to_subtract = int(days_to_subtract_key.split("=")[1])
            print(days_to_subtract,year,dt,st,iw,ran,method)
            rankings = self.rankings_df.loc[days_to_subtract,year,dt,st,iw,ran,method].dropna() #spec_best_pred_df = best_pred_df.set_index(['Year','days_to_subtract_key',"Method"]).loc[[(year,days_to_subtract_key,method)]]
            for i,D in enumerate(X.loc[(year,days_to_subtract_key,dt,st,iw,ran,method),"D"]):
                if sum_D is None:
                    sum_D = D
                else:
                    sum_D = sum_D.add(iw*D,fill_value=0)
                if i == 0:
                    construction = "Direct"
                elif i == 1:
                    construction = "Indirect"
                else:
                    raise Exception("Error")
                features = pyrplib.utils.compute_features(D, rankings, self.top_k, self.feature_columns)
                features.name = tuple(list(index)+[construction])
                X_new = X_new.append(features)

                if i == 1:
                    construction = "Both"
                    features = pyrplib.utils.compute_features(sum_D, rankings, self.top_k, self.feature_columns)
                    features.name = tuple(list(index)+[construction])
                    X_new = X_new.append(features)
        return X_new


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

# +
#class ComputeFeaturesTransformer( BaseEstimator, TransformerMixin ):
#    def __init__(self, rankings, top_k, feature_columns):
#        self.rankings = rankings
#        self.top_k = top_k
#        self.feature_columns = feature_columns
#        
#    def fit( self, X, y = None ):
#        return self
#    
#    def transform(self, D, y = None ):
#        top_teams = list(rankings.sort_values().index[:top_k])
#        D = D.loc[top_teams,top_teams]
#        delta_lop,details_lop = pyrankability.rank.solve(D.fillna(0),method='lop',cont=True)
#
#        x = pd.DataFrame(details_lop['x'],index=D.index,columns=D.columns)
#        r = x.sum(axis=0)
#        order = np.argsort(r)
#        xstar = x.iloc[order,:].iloc[:,order]
#        xstar.loc[:,:] = pyrankability.common.threshold_x(xstar.values)
#        inxs = np.triu_indices(len(xstar),k=1)
#        xstar_upper = xstar.values[inxs[0],inxs[1]]
#        nfrac_upper_lop = sum((xstar_upper > 0) & (xstar_upper < 1))
#
#        top_teams = xstar.columns[:top_k]
#
#        k_two_distant,details_two_distant = pyrankability.search.solve_pair_max_tau(D.fillna(0),method='lop',cont=False,verbose=False)
#        d_lop = details_two_distant['tau']
#
#        delta_hillside,details_hillside = pyrankability.rank.solve(D,method='hillside',cont=True)
#
#        x = pd.DataFrame(details_hillside['x'],index=D.index,columns=D.columns)
#        r = x.sum(axis=0)
#        order = np.argsort(r)
#        xstar = x.iloc[order,:].iloc[:,order]
#        xstar.loc[:,:] = pyrankability.common.threshold_x(xstar.values)
#        inxs = np.triu_indices(len(xstar),k=1)
#        xstar_upper = xstar.values[inxs[0],inxs[1]]
#        nfrac_upper_hillside = sum((xstar_upper > 0) & (xstar_upper < 1))
#
#        top_teams = xstar.columns[:top_k]
#
#        k_two_distant,details_two_distant = pyrankability.search.solve_pair_max_tau(D,method='hillside',verbose=False,cont=False)
#        d_hillside = details_two_distant['tau']
#
#        features = pd.Series([delta_lop,delta_hillside,2*nfrac_upper_lop,2*nfrac_upper_hillside,d_lop,d_hillside],index=feature_columns)
#
#        return features
# -

"""
target = problem['target'].groupby(['days_to_subtract1','days_to_subtract2','Method','Year','direct_thres','spread_thres','weight_indirect'])[feature_names].mean()
target
"""


class GroupByTransformer( BaseEstimator, TransformerMixin ):
    def __init__(self, group_cols, feature_names):
        self.group_cols = group_cols
        self.feature_names = feature_names
        
    def fit( self, X, y = None ):
        return self
    
    def transform( self, problem, y = None ):
        target = problem['target'].groupby([group_cols])[feature_names].mean()
        return target


# ### Generate 0001

# +

"""
outer_keys = list(itertools.product(domains_ranges,years))
for domain_range,year in tqdm(outer_keys):
    # set the team_domain
    team_domain = None
    if domain_range[0] == 'madness':
        team_domain = madness_teams[year]
    elif domain_range[0] == 'all':
        team_domain = all_teams[year]

    # set the team_range
    team_range = None
    if domain_range[1] == 'madness':
        team_range = madness_teams[year]
    elif domain_range[1] == 'all':
        team_range = all_teams[year]

    columns = ["days_to_subtract","direct_thres","spread_thres","weight_indirect"]+team_range
    massey_rankings[(domain_range,year)] = pd.DataFrame(columns=columns)
    colley_rankings[(domain_range,year)] = pd.DataFrame(columns=columns)
    massey_rs[(domain_range,year)] = pd.DataFrame(columns=columns)
    colley_rs[(domain_range,year)] = pd.DataFrame(columns=columns)
    massey_perms[(domain_range,year)] = pd.DataFrame(columns=columns)
    colley_perms[(domain_range,year)] = pd.DataFrame(columns=columns)

    game_df = pd.DataFrame({"team1_name":games[year]['team1_name'],
                            "team1_score":games[year]['points1'],
                            "team1_H_A_N": games[year]['H_A_N1'],
                            "team2_name":games[year]['team2_name'],
                            "team2_score":games[year]['points2'],
                            "team2_H_A_N": games[year]['H_A_N1'],
                            "date": games[year]['date']
                           }).sort_values(by='date')#.drop('date',axis=1)
    mask = game_df.team1_name.isin(team_domain) & game_df.team2_name.isin(team_domain)
    game_df = game_df.loc[mask]
"""
# -

class GenGameDfTransformer( BaseEstimator, TransformerMixin ):
    def __init__(self, outer_keys, event, event_teams, columns):
        self.outer_keys = outer_keys
        self.event = event
        self.event_teams = event_teams
        self.columns = columns
        
    def fit( self, X, y = None ):
        return self
    
    def transform( self, X, y = None ): # not sure what should be passed in here for X
        for domain_range,year in tqdm(outer_keys):
            # set the team_domain
            team_domain = None
            if domain_range[0] == event:
                team_domain = event_teams[year]
            elif domain_range[0] == 'all':
                team_domain = all_teams[year]

            # set the team_range
            team_range = None
            if domain_range[1] == event:
                team_range = event_teams[year]
            elif domain_range[1] == 'all':
                team_range = all_teams[year]

            columns = ["days_to_subtract","direct_thres","spread_thres","weight_indirect"]+team_range
            massey_rankings[(domain_range,year)] = pd.DataFrame(columns=columns)
            colley_rankings[(domain_range,year)] = pd.DataFrame(columns=columns)
            massey_rs[(domain_range,year)] = pd.DataFrame(columns=columns)
            colley_rs[(domain_range,year)] = pd.DataFrame(columns=columns)
            massey_perms[(domain_range,year)] = pd.DataFrame(columns=columns)
            colley_perms[(domain_range,year)] = pd.DataFrame(columns=columns)

            game_df = pd.DataFrame({"team1_name":games[year]['team1_name'],
                                    "team1_score":games[year]['points1'],
                                    "team1_H_A_N": games[year]['H_A_N1'], # what is this?
                                    "team2_name":games[year]['team2_name'],
                                    "team2_score":games[year]['points2'],
                                    "team2_H_A_N": games[year]['H_A_N1'],
                                    "date": games[year]['date']
                                   }).sort_values(by='date')#.drop('date',axis=1)
            mask = game_df.team1_name.isin(team_domain) & game_df.team2_name.isin(team_domain)
            game_df = game_df.loc[mask]
            
        return game_df


# ### US News

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

class ColumnSumTransformer( BaseEstimator, TransformerMixin ):
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
            for i in range(len(sorted_col)-1):
                D.loc[sorted_col.index[i], sorted_col.index[i+1:]] += -(sorted_col.iloc[i] - sorted_col.iloc[i+1])
        return D

class ColumnCountTransformer( BaseEstimator, TransformerMixin ):
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


