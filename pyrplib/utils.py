#!/usr/bin/env python
# coding: utf-8
# %%

# # A Utility Library for Rankability Problems

# %%


import pandas as pd
import numpy as np
import itertools
import pyrankability
import altair as alt
from IPython.display import display, Markdown, Latex


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


# %%
def get_pairs_by_width(X_for_join):
    pairs_by_width = {}
    for f1,f2 in itertools.combinations(X_for_join['days_to_subtract1'].unique().astype(int),2):
        if f2 < f1:
            f1,f2 = f2,f1
        width = f2-f1#round(100*(f2-f1))
        if width not in pairs_by_width:
            pairs_by_width[width] = []
        pairs_by_width[width].append((f1,f2))
        
    return pairs_by_width


# %%
def get_graph_dfs(index_cols, feature_columns, feature_names, pairs_by_width, Xy):
    graph_dfs = {}
    for target_column in feature_names:
        graph_df = pd.DataFrame(columns=index_cols+feature_columns).set_index(index_cols)

        for width in pairs_by_width.keys():
            summary = None
            for pair in pairs_by_width[width]:
                data = Xy.set_index(['days_to_subtract1','days_to_subtract2']).loc[pair].reset_index()
                for_corr = data.set_index(['Method','Construction',"days_to_subtract1","days_to_subtract2"])
                if summary is None:
                    summary = pd.DataFrame(columns=["days_to_subtract1","days_to_subtract2","Method","Construction"]+feature_columns).set_index(list(for_corr.index.names))
                for ix in for_corr.index.unique():
                    corr_results = for_corr.loc[ix][[target_column]+feature_columns].corr()
                    target_corr_results = corr_results.loc[target_column].drop(target_column)
                    target_corr_results.name = ix
                    summary = summary.append(target_corr_results)

            graph_df1 = summary.reset_index()
            graph_df1['width'] = width
            graph_df1 = graph_df1.set_index(index_cols)
            graph_df = graph_df.append(graph_df1)
        graph_dfs[target_column]=graph_df
        
    for key in graph_dfs.keys():
        graph_dfs[key] = graph_dfs[key].reset_index()
        
    return graph_dfs


# %%
def display_graph_dfs(graph_dfs, feature_columns, index_cols):
    for key in graph_dfs.keys():
        display(Markdown(f'## {key}'))
        graph_df = graph_dfs[key].melt(value_vars=feature_columns,id_vars=index_cols,value_name='Value',var_name='Feature')

        display(Markdown('### Colley'))
        g = alt.Chart(graph_df.set_index('Method').loc['Colley']).mark_bar().encode(
            x='width:N',
            y=alt.Y('average(Value)',scale=alt.Scale(domain=[-.6, .6])),
            row='Feature:N',
            color='Construction:N',
            column='Construction:N'
        )
        display(g)

        display(Markdown('### Massey'))
        g = alt.Chart(graph_df.set_index('Method').loc['Massey']).mark_bar().encode(
            x='width:N',
            y=alt.Y('average(Value)',scale=alt.Scale(domain=[-.6, .6])),
            row='Feature:N',
            color='Construction:N',
            column='Construction:N'
        )
        display(g)
