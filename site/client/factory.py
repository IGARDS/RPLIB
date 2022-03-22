import requests
import io
import sys
import traceback
import os
import base64
from pathlib import Path
import json
import diskcache
import zipfile
import tempfile
import os
import urllib

import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.long_callback import DiskcacheLongCallbackManager
import pandas as pd
import numpy as np
import altair as alt
from dash.dependencies import Input, Output, State

import pyrplib

from .common import *
from .identifier import *
from . import load

RPLIB_DATA_PREFIX = os.environ.get("RPLIB_DATA_PREFIX")

# Config contains all of the datasets and other configuration details
config = pyrplib.data.Data(RPLIB_DATA_PREFIX)

cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

BASE_PATH = os.getenv("BASE_PATH","/")
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP],url_base_pathname=BASE_PATH, long_callback_manager=long_callback_manager)
print("BASE_PATH",BASE_PATH)
server = app.server

# the style arguments for the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "12rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position to the right of the sidebar
CONTENT_STYLE = {
    "margin-left": "12rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("RP Lib", className="display-4"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Unprocessed", href=f"{BASE_PATH}", active="exact"),
                dbc.NavLink("Processed", href=f"{BASE_PATH}processed", active="exact"),
                dbc.NavLink("LOP", href=f"{BASE_PATH}lop", active="exact"),
                dbc.NavLink("Hillside", href=f"{BASE_PATH}hillside", active="exact"),
                dbc.NavLink("Colley", href=f"{BASE_PATH}colley", active="exact"),
                dbc.NavLink("Massey", href=f"{BASE_PATH}massey", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Artificial Structured Datasets", href="https://colab.research.google.com/drive/1nNsf_bVFMw3q9Eq2qBYv9qxmrlIqpGJU?usp=sharing", active="exact"),
                dbc.NavLink("Contribute Dataset", href="https://docs.google.com/forms/d/e/1FAIpQLSenO1WO_LlzNQ1ak4IPyOjBKkuixZU93umLgeI2kJbFxwzcZQ/viewform", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)
  

df_datasets = load.get_datasets(config)

df_processed = load.get_processed(config)

df_lop_cards = load.get_cards(config, Method.LOP)

df_hillside_cards = load.get_cards(config, Method.HILLSIDE)

df_massey_cards = load.get_cards(config, Method.MASSEY)

df_colley_cards = load.get_cards(config, Method.COLLEY)

unprocessed_table = pyrplib.style.get_standard_data_table(df_datasets, UNPROCESSED_TABLE_ID)
unprocessed_download_button = \
    pyrplib.style.get_standard_download_all_button(UNPROCESSED_TABLE_DOWNLOAD_ALL_BUTTON_ID, 
                                                   UNPROCESSED_TABLE_DOWNLOAD_ALL_ID,
                                                   UNPROCESSED_TABLE_DOWNLOAD_PROGRESS_ID,
                                                   UNPROCESSED_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID)
page_unprocessed = html.Div([
    html.H1("Unprocessed Datasets"),
    html.P("Search for an unprocessed dataset with filtered fields (case sensitive). Select a row by clicking. Results will be shown below the table."),
    unprocessed_download_button,
    unprocessed_table,
    html.Br(),
    html.H2("Selected content will appear below"),
    html.Div(id="datasets_output")
])

processed_table = pyrplib.style.get_standard_data_table(df_processed, PROCESSED_TABLE_ID)
processed_download_button = \
    pyrplib.style.get_standard_download_all_button(PROCESSED_TABLE_DOWNLOAD_ALL_BUTTON_ID, 
                                                   PROCESSED_TABLE_DOWNLOAD_ALL_ID, 
                                                   PROCESSED_TABLE_DOWNLOAD_PROGRESS_ID,
                                                   PROCESSED_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID)

processed_table = pyrplib.style.get_standard_data_table(df_processed, "processed_table")
page_processed = html.Div([
    html.H1("Processed Datasets"),
    html.P("Search for a dataset with filtered fields (case sensitive). Select a row by clicking. Results will be shown below the table."),
    processed_download_button,
    processed_table,
    html.Br(),
    html.H2("Selected content will appear below"),
    html.Div(id="processed_output")
])

lop_table = pyrplib.style.get_standard_data_table(df_lop_cards, LOP_TABLE_ID)
lop_download_button = \
    pyrplib.style.get_standard_download_all_button(LOP_TABLE_DOWNLOAD_ALL_BUTTON_ID, 
                                                   LOP_TABLE_DOWNLOAD_ALL_ID,
                                                   LOP_TABLE_DOWNLOAD_PROGRESS_ID,
                                                   LOP_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID)
page_lop = html.Div([
    html.H1("Search LOP Solutions and Analysis (i.e., LOP cards)"),
    html.P("Search for LOP card with filtered fields (case sensitive). Select a row by clicking. Results will be shown below the table."),
    lop_download_button,
    lop_table,
    html.Br(),
    html.H2("Selected content will appear below"),
    html.Div(id="lop_output")
])

hillside_table = pyrplib.style.get_standard_data_table(df_hillside_cards, HILLSIDE_TABLE_ID)
page_hillside = html.Div([
    html.H1("Search Hillside Solutions and Analysis"),
    html.P("Search for a Hillside Card with filtered fields (case sensitive). Select a row by clicking. Results will be shown below the table."),
    hillside_table,
    html.Div(id="hillside_output")
    ])

massey_table = pyrplib.style.get_standard_data_table(df_massey_cards, MASSEY_TABLE_ID)
page_massey = html.Div([
    html.H1("Search Massey Solutions and Analysis"),
    html.P("Search for a Massey Card with filtered fields (case sensitive). Select a row by clicking. Results will be shown below the table."),
    massey_table,
    html.Div(id="massey_output")
    ])

colley_table = pyrplib.style.get_standard_data_table(df_colley_cards, COLLEY_TABLE_ID)
page_colley = html.Div([
    html.H1("Search Colley Solutions and Analysis"),
    html.P("Search for a Colley Card with filtered fields (case sensitive). Select a row by clicking. Results will be shown below the table."),
    colley_table,
    html.Div(id="colley_output")
    ])


def get_blank_page(page_name):
    return html.Div([
    html.H1(f"Search {page_name} Solutions and Analysis"),
    html.P("This is currently empty."),
    html.Div(id="output")
    ])

def get_404(pathname):
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(
                f"The pathname {pathname} was not recognised...")
        ]
    )

# components for all pages
content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

@app.callback(
    Output("page-content", "children"), 
    [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == f"{BASE_PATH}":
        return page_unprocessed
    elif pathname == f"{BASE_PATH}processed":
        return page_processed
    elif pathname == f"{BASE_PATH}lop":
        return page_lop
    elif pathname == f"{BASE_PATH}hillside":
        return page_hillside
    elif pathname == f"{BASE_PATH}massey":
        return page_massey
    elif pathname == f"{BASE_PATH}colley":
        return page_colley
    elif os.path.exists(pathname):
        return get_download_local_file_button(pathname)

    # if the user tries to reach a different page, return a 404 message
    return get_404(pathname)

#setup_cell_clicked_dataset

if __name__ == "__main__":
    app.run_server(port=8888)
