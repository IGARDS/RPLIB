import os

import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go


import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)
server = app.server

import sys
from pathlib import Path
home = str(Path.home())

sys.path.insert(0,"%s/ranking_toolbox"%home)
sys.path.insert(0,"%s/RPLib"%home)
sys.path.insert(0,"%s/fairness_analysis"%home)

import pyrankability
import pyrplib


import json
Ds = pd.read_json(f'{home}/us_news_world_report_study/results/Ds.json')

def generate_table(dataframe, max_rows=26):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns]) ] +
        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

app.layout = html.Div(children=[
    html.H4(children='D'),
    generate_table(pd.DataFrame(Ds['D'].iloc[0]))
])

if __name__ == '__main__':

    app.run_server(debug=True)