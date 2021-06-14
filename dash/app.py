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
    return html.Img(src=img_b64, style={'height': '30%', 'width': '30%'})

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


# +
#key = (2002, 'Student')
# -

def generate_table(dataframe, max_rows=26):
    return dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in dataframe.columns],
        data=dataframe.to_dict('records'),
    )

app.layout = html.Div(children=[
    html.H1("Visualizing the Rankability of US News & World Report", style={'text-align': 'center'}),
    html.H4(children='D Matrix'),
    generate_table(Ds.loc[(2002, 'Student'),'D']),
    html.Br(),
    html.H4(children='Spider Plot'),
        dcc.Dropdown(id="select_group",
                 options=[
                     {"label": "Student", "value": 'Student'},
                     {"label": "Parent", "value": 'Parent'},
                     {"label": "Both", "value": 'Both'}],
                 multi=False,
                 value="Student",
                 style={'width': "40%"}
                 ),
    
    #html_image(open('/tmp/spider3.png','rb').read()),
    html.Img(id="spider_img", children=[]),
    html.Br()
], style={'textAlign': 'center'})


# +
@app.callback(
     Output(component_id='spider_img', component_property='children'),
    Input(component_id='select_group', component_property='value')
)

def update_graph(group):
    key = (2002, group)
    print(key)
    A = perm_to_series(Ds.loc[key,'D'],Ds.loc[key,'details_fixed_cont_x_minimize']['perm'],'Closest')
    B = perm_to_series(Ds.loc[key,'D'],Ds.loc[key,'details_fixed_cont_x_maximize']['perm'],'Farthest')
    pyrankability.plot.spider2(A,B,file='/tmp/spider3.png')
    print(type(html_image(open('/tmp/spider3.png','rb').read())))
    return html_image(open('/tmp/spider3.png','rb').read())
