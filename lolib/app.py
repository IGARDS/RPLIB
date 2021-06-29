import os
import glob

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
    return html.Img(src=img_b64, style={'width': '100%'})

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

records = []
files = glob.glob(f'{home}/lolib_study/results/IO/*.json')
for file in files:
    records.append(pd.Series(json.loads(open(file).read())))
records = pd.concat(records,axis=1).T
print(records.loc[0,"solutions"]['0'])

def generate_table(dataframe, max_rows=26):
    return dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in dataframe.columns],
        data=dataframe.to_dict('records'),
    )

app.layout = html.Div([
    html.H6("Enter the LOLIB instance to display the number of solutions: %s"%(",".join(records['file']))),
    html.Div(["Input: ",
              dcc.Input(id='my-input', value='initial value', type='text')]),
    html.Br(),
    html.Div(id='my-output'),
    html.Div(generate_table(records.drop('solutions',axis=1)))
])


@app.callback(
    Output(component_id='my-output', component_property='children'),
    Input(component_id='my-input', component_property='value')
)
def update_output_div(input_value):
    number_solutions = len(records.set_index('file').loc[input_value,'solutions'].keys())
    solutions = records.set_index('file').loc[input_value,'solutions']
    P = []
    for key in solutions.keys():
        P.append(solutions[key]['details']['P'][0])
    return 'Number of solutions: {}'.format(number_solutions) + "\n" + str(P)