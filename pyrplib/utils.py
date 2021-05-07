#!/usr/bin/env python
# coding: utf-8
# %%

# # A Utility Library for Rankability Problems

# %%


import pandas as pd
import numpy as np
import itertools
import pyrankability


# ## Problem 1

# %%


# Constructs a dataframe from selected parameters
# columns is a dictionary of form {col_name: col_value}
def get_sel_df(columns):
    sel_df = pd.DataFrame(columns=list(columns.keys()))
    c = 0
    print(list(columns.values()))
    for values in itertools.product(*columns.values()):
        print(values)
        sel_df = sel_df.append(pd.Series(values, index=sel_df.columns, name=c))
        c += 1

    return sel_df


# %%


def filter_teams(games, remaining_games, teams_by_year):
    for year, teams in teams_by_year.items():
        team1_name = games[year].team1_name
        team2_name = games[year].team2_name
        games[year] = games[year].loc[team1_name.isin(teams) | team2_name.isin(teams)]

        team1_name = remaining_games[year].team1_name
        team2_name = remaining_games[year].team2_name
        remaining_games[year] = remaining_games[year].loc[team1_name.isin(teams) | team2_name.isin(teams)]
        
    return games, remaining_games


# %%
def compute_features(D, rankings, top_k, feature_columns):
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
    
    k_two_distant,details_two_distant = pyrankability.search.solve_pair(D.fillna(0),method='lop',minimize=False,verbose=False)
    d_lop = k_two_distant#details_two_distant['tau']
    
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
    
    k_two_distant,details_two_distant = pyrankability.search.solve_pair(D,method='hillside',minimize=False,verbose=False)
    d_hillside = k_two_distant#details_two_distant['tau']
    
    features = pd.Series([delta_lop,delta_hillside,2*nfrac_upper_lop,2*nfrac_upper_hillside,d_lop,d_hillside],index=feature_columns)

    return features
