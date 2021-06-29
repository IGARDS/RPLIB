import os

import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go


import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table

from base64 import b64encode


def html_image(img_bytes):
    encoding = b64encode(img_bytes).decode()
    img_b64 = "data:image/png;base64," + encoding
    return img_b64
    #return html.Img(src=img_b64, style={'height': '30%', 'width': '30%'})

app = dash.Dash(__name__)
server = app.server

import sys
from pathlib import Path
home = str(Path.home())

sys.path.insert(0,"%s/ranking_toolbox"%home)
sys.path.insert(0,"%s/RPLib"%home)

import pyrankability
import pyrplib

import json
Ds = pd.read_json(f'{home}/us_news_world_report_study/results/Ds.json',orient='records')
def process(Ds):
    Ds2 = Ds.set_index(['Year','Group']).copy()
    D = Ds['D']
    new_D = []
    for index in D.index:
        D_ = pd.DataFrame(D[index])
        D_.index = D_.columns
        new_D.append(D_)
    Ds2.loc[:,'D'] = new_D
    return Ds2

def perm_to_series(D,perm,name):
    return pd.Series(list(D.index[list(perm)]),name=name)

Ds = process(Ds)
Ds


def generate_table(dataframe, max_rows=26):
    return dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in dataframe.columns],
        data=dataframe.to_dict('records'),
    )

app.layout = html.Div(children=[
    html.H1("Visualizing the Rankability of US News & World Report University Rankings", style={'text-align': 'center'}),
    html.H3(children='D Matrix'),
    generate_table(Ds.loc[(2002, 'Student'),'D']),
    html.Br(),
    html.H3(children='Spider Plots'),
        dcc.Dropdown(id="select_group",
                 options=[
                     {"label": "Student", "value": 'Student'},
                     {"label": "Parent", "value": 'Parent'},
                     {"label": "Both", "value": 'Both'}],
                 multi=False,
                 value="Student",
                 style={'width': "40%"}
                 ),
    
    html.Img(title="Test Title Tag", id="spider_img", style={'height': '30%', 'width': '30%'}),
    html.Img(id="spider_img2", style={'height': '30%', 'width': '30%'}),
    html.Img(id="spider_img3", style={'height': '30%', 'width': '30%'})
], style={'textAlign': 'center'})


# +
@app.callback(
    [Output(component_id='spider_img', component_property='src'),
     Output(component_id='spider_img2', component_property='src'),
    Output(component_id='spider_img3', component_property='src')],
    Input(component_id='select_group', component_property='value')
)

def update_graph(group):
    key = (2002, group)
    
    # fixed min/max spider
    A = perm_to_series(Ds.loc[key,'D'],Ds.loc[key,'details_fixed_cont_x_minimize']['perm'],'Closest')
    B = perm_to_series(Ds.loc[key,'D'],Ds.loc[key,'details_fixed_cont_x_maximize']['perm'],'Farthest')
    pyrankability.plot.spider2(A,B,file='/tmp/fixed_min_max_spider.png')
    
    # pair min/min spider
    A = perm_to_series(Ds.loc[key,'D'],Ds.loc[key,'details_pair_minimize']['perm_x'],'Closest')
    B = perm_to_series(Ds.loc[key,'D'],Ds.loc[key,'details_pair_minimize']['perm_y'],'Farthest')
    filepath = '/tmp/fixed_min_max_spider.png'
    pyrankability.plot.spider2(A,B,file='/tmp/pair_minimize_spider.png')
    
    # pair max/max spider
    A = perm_to_series(Ds.loc[key,'D'],Ds.loc[key,'details_pair_maximize']['perm_x'],'Closest')
    B = perm_to_series(Ds.loc[key,'D'],Ds.loc[key,'details_pair_maximize']['perm_y'],'Farthest')
    pyrankability.plot.spider2(A,B,file='/tmp/pair_maximize_spider.png')
    return html_image(open('/tmp/fixed_min_max_spider.png','rb').read()), \
        html_image(open('/tmp/pair_minimize_spider.png','rb').read()), \
        html_image(open('/tmp/pair_maximize_spider.png','rb').read())
