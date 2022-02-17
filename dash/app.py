import requests
import io
import sys
import traceback
import os
import base64
from io import BytesIO
from pathlib import Path
import json
from enum import Enum

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import altair as alt
from dash.dependencies import Input, Output, State
import urllib

home = str(Path.home())

RPLIB_DATA_PREFIX = os.environ.get("RPLIB_DATA_PREFIX")

if RPLIB_DATA_PREFIX is None: # Set default
    RPLIB_DATA_PREFIX=f'{home}/RPLib/data'
    
try:
    import pyrankability as pyrankability
    import pyrplib as pyrplib
except:
    print('Looking for packages in home directory')
    sys.path.insert(0,f"{home}") # Add the home directory relevant paths to the PYTHONPATH
    sys.path.insert(0,f"{home}/ranking_toolbox") # Add the home directory relevant paths to the PYTHONPATH
    sys.path.insert(0,f"{home}/RPLib") # Add the home directory relevant paths to the PYTHONPATH
    import pyrankability
    import pyrplib
    
# Config contains all of the datasets and other configuration details
config = pyrplib.config.Config(RPLIB_DATA_PREFIX)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
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
                dbc.NavLink("Unprocessed", href="/", active="exact"),
                dbc.NavLink("Processed", href="/processed", active="exact"),
                dbc.NavLink("LOP", href="/lop", active="exact"),
                dbc.NavLink("Hillside", href="/hillside", active="exact"),
                dbc.NavLink("Colley", href="/colley", active="exact"),
                dbc.NavLink("Massey", href="/massey", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Artificial Structured Datasets", href="https://colab.research.google.com/drive/1nNsf_bVFMw3q9Eq2qBYv9qxmrlIqpGJU?usp=sharing", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

def get_datasets(config):
    df2 = config.datasets_df.copy()
    
    def process(links):
        try:
            if type(links) != list:
                links = [links]
            res = ", ".join(["[%s](%s)"%(link.split("/")[-1],link) for link in links])
            return res
        except:
            return "Could not process. Check data."

    df2['Download links'] = df2['Download links'].apply(process)
    df2 = df2.drop('Loader',axis=1).drop('Description',axis=1)
    
    df2 = df2.sort_values(by='Dataset Name')
    
    return df2

def get_processed(config):
    datasets_df = df = config.datasets_df.set_index('Dataset ID')
    df = config.processed_datasets_df.copy()
            
    def process(row):
        entry = pd.Series(index=['Dataset ID','Source Dataset ID','Source Dataset Name','Short Type','Type','Command','Size','Download'])
        link = row['Link']
        entry['Dataset ID'] = row['Dataset ID']
        if row['Type'] == "D":
            try:
                d = pyrplib.dataset.ProcessedD.from_json(link).load()
                entry.loc['Source Dataset ID'] = d.source_dataset_id
                entry.loc['Source Dataset Name'] = datasets_df.loc[d.source_dataset_id,"Dataset Name"]
                entry.loc['Dataset ID'] = d.dataset_id
                entry.loc['Short Type'] = d.short_type
                entry.loc['Type'] = d.type
                entry.loc['Command'] = d.command
                entry.loc['Size'] = d.data.shape
                entry.loc['Download'] = "[%s](%s)"%(link.split("/")[-1],link)
            except Exception as e:
                print(row)
                print("Exception in get_processed:",e)
                print(traceback.format_exc())
        return entry

    datasets = df.apply(process,axis=1)
    
    return datasets

def get_cards(config, method):
    if method == Method.LOP:
        df = config.lop_cards_df.copy()
    elif method == Method.HILLSIDE:
        df = config.hillside_cards_df.copy() 
        return df
    elif method == Method.MASSEY:
        df = config.massey_cards_df.copy()
        return df
    elif method == Method.COLLEY:
        df = config.colley_cards_df.copy()
        return df
    else:
        raise ValueError('No valid card was requested from options: lop, hillside, massey, or colley')
        
    def process(row):
        entry = pd.Series(index=['Dataset ID','Unprocessed Dataset Name','Shape of D','Objective','Found Solutions','Download'])
        link = row['Link']
        entry['Dataset ID'] = row['Dataset ID']
        try:
            card = pyrplib.card.LOP.from_json(link)
            datasets_df = config.datasets_df.set_index('Dataset ID')
            processed_datasets_df = config.processed_datasets_df.set_index('Dataset ID') 
            dataset_name = datasets_df.loc[processed_datasets_df.loc[card.source_dataset_id,"Source Dataset ID"],"Dataset Name"]
        
            entry.loc['Unprocessed Dataset Name'] = dataset_name
            entry.loc['Dataset ID'] = card.dataset_id
            D = card.D
            entry.loc['Shape of D'] = ",".join([str(n) for n in D.shape])
            entry.loc['Objective'] = card.obj
            entry.loc['Found Solutions'] = len(card.solutions)
            entry.loc['Download'] = "[%s](%s)"%(link.split("/")[-1],link)
        except Exception as e:
            print("Exception in get_lop_cards:",e)
            print(traceback.format_exc())
        return entry

    cards = df.apply(process,axis=1)
        
    return cards

class Method(Enum):
    LOP = 0
    HILLSIDE = 1
    MASSEY = 2
    COLLEY = 3  

df_datasets = get_datasets(config)

df_processed = get_processed(config)

df_lop_cards = get_cards(config, Method.LOP)

df_hillside_cards = get_cards(config, Method.HILLSIDE)

df_massey_cards = get_cards(config, Method.MASSEY)

df_colley_cards = get_cards(config, Method.COLLEY)

# Create dash tables and actions
style_data_conditional = [
    {
        "if": {"state": "active"},
        "backgroundColor": "rgba(150, 180, 225, 0.2)",
        "border": "1px solid blue",
    },
    {
        "if": {"state": "selected"},
        "backgroundColor": "rgba(0, 116, 217, .03)",
        "border": "1px solid blue",
    },
]

## Unprocessed data first
def update_selected_row_color(active):
    style = style_data_conditional.copy()
    if active:
        style.append(
            {
                "if": {"row_index": active["row"]},
                "backgroundColor": "rgba(150, 180, 225, 0.2)",
                "border": "1px solid blue",
            },
        )
    return style

dataset_table = pyrplib.style.get_standard_data_table(df_datasets,"datasets_table")

page_datasets = html.Div([
    html.H1("Unprocessed Datasets"),
    html.P("Search for an unprocessed dataset with filtered fields (case sensitive). Select a row by clicking. Results will be shown below the table."),
    dataset_table,
    html.Br(),
    html.H2("Selected content will appear below"),
    html.Div(id="datasets_output")
])

@app.callback(
    Output("datasets_output", "children"),
    Input("datasets_table", "active_cell"),
    State("datasets_table", "derived_viewport_data"),
)
def cell_clicked_dataset(cell,data):
    if cell is None:
        return dash.no_update
    row,col = cell["row"],cell["column_id"]
    selected = data[row][col]
    dataset_id = data[row]['Dataset ID']
    dataset_name = data[row]['Dataset Name']
    datasets_df = config.datasets_df.set_index('Dataset ID')
    links = datasets_df.loc[dataset_id,'Download links']
    loader = datasets_df.loc[dataset_id,'Loader']
    description = datasets_df.loc[dataset_id,'Description']
    if selected is not None:
        import importlib
        loader_lib = ".".join(loader.split(".")[:-1])
        cls_str = loader.split(".")[-1]
        load_lib = importlib.import_module(f"pyrplib.{loader_lib}")
        cls = getattr(load_lib, cls_str)
        unprocessed = cls(dataset_id,links).load()
        contents = [html.Br(),html.H2(dataset_name),html.P(description),]+[unprocessed.view()]
        return html.Div(contents)
    else:
        return dash.no_update  

@app.callback(
    Output("datasets_table", "style_data_conditional"),
    [Input("datasets_table", "active_cell")]
)
def update_selected_row_color_dataset(active):
    return update_selected_row_color(active)

@app.callback(
    Output("processed_output", "children"),
    Input("processed_table", "active_cell"),
    State("processed_table", "derived_viewport_data"),
)
def cell_clicked_processed(cell,data):
    if cell is None:
        return dash.no_update
    row,col = cell["row"],cell["column_id"]
    selected = data[row][col]
    if selected is not None:
        dataset_id = data[row]['Dataset ID']
        link = config.processed_datasets_df.set_index('Dataset ID').loc[dataset_id,"Link"]
        options = config.processed_datasets_df.set_index('Dataset ID').loc[dataset_id,"Options"]
        if type(options) == str:
            options = json.loads(options)
            options_str = json.dumps(options,indent=2)
        else:
            options_str = "None"
        short_type = data[row]['Short Type']
        if short_type == "D":
            obj = pyrplib.dataset.ProcessedD.from_json(link).load()
        datasets_df = config.datasets_df.set_index('Dataset ID')
        description = datasets_df.loc[obj.source_dataset_id,"Description"]
        dataset_name = datasets_df.loc[obj.source_dataset_id,"Dataset Name"]
        command = obj.command
        contents = [html.Br(),html.H2("Source Dataset Name"),html.P(dataset_name),html.H2("Description"),html.P(description),html.H2("Command"),html.P(command),html.H2("Options"),html.Pre(options_str)]+[obj.view()]
        return html.Div(contents)
    else:
        return dash.no_update  

@app.callback(
    Output("processed_table", "style_data_conditional"),
    [Input("processed_table", "active_cell")]
)
def update_selected_row_color_processed(active):
    return update_selected_row_color(active)

@app.callback(
    Output("lop_output", "children"),
    Input("lop_table", "active_cell"),
    State("lop_table", "derived_viewport_data"),
)
def cell_clicked_lop(cell,data):
    if cell is None:
        return dash.no_update
    row,col = cell["row"],cell["column_id"]
    selected = data[row][col]
    if selected is not None:
        dataset_id = data[row]['Dataset ID']
        link = config.lop_cards_df.set_index('Dataset ID').loc[dataset_id,"Link"]
        options = config.lop_cards_df.set_index('Dataset ID').loc[dataset_id,"Options"]
        if type(options) == str:
            options = json.loads(options)
            options_str = json.dumps(options,indent=2)
        else:
            options_str = "None"
        obj = pyrplib.card.LOP.from_json(link)
        
        processed_datasets_df = config.processed_datasets_df.set_index('Dataset ID') 
        datasets_df = config.datasets_df.set_index('Dataset ID') 
        description = datasets_df.loc[processed_datasets_df.loc[obj.source_dataset_id,"Source Dataset ID"],"Description"]
        dataset_name = datasets_df.loc[processed_datasets_df.loc[obj.source_dataset_id,"Source Dataset ID"],"Dataset Name"]
        
        contents = [html.Br(),html.H2("Source Dataset Name"),html.P(dataset_name),html.H2("Description"),html.P(description),html.H2("Options"),html.Pre(options_str)]+obj.view()
        return html.Div(contents)
    else:
        return dash.no_update  
    
@app.callback(
    Output("lop_table", "style_data_conditional"),
    [Input("lop_table", "active_cell")]
)
def update_selected_row_color_lop(active):
    return update_selected_row_color(active)

processed_table = pyrplib.style.get_standard_data_table(df_processed, "processed_table")
page_processed = html.Div([
    html.H1("Processed Datasets"),
    html.P("Search for a dataset with filtered fields (case sensitive). Select a row by clicking. Results will be shown below the table."),
    processed_table,
    html.Br(),
    html.H2("Selected content will appear below"),
    html.Div(id="processed_output")
])

lop_table = pyrplib.style.get_standard_data_table(df_lop_cards,"lop_table")
page_lop = html.Div([
    html.H1("Search LOP Solutions and Analysis (i.e., LOP cards)"),
    html.P("Search for LOP card with filtered fields (case sensitive). Select a row by clicking. Results will be shown below the table."),
    lop_table,
    html.Br(),
    html.H2("Selected content will appear below"),
    html.Div(id="lop_output")
])

hillside_table = pyrplib.style.get_standard_data_table(df_hillside_cards,"hillside_table")
page_hillside = html.Div([
    html.H1("Search Hillside Solutions and Analysis"),
    html.P("Search for a Hillside Card with filtered fields (case sensitive). Select a row by clicking. Results will be shown below the table."),
    hillside_table,
    html.Div(id="output")
    ])

massey_table = pyrplib.style.get_standard_data_table(df_massey_cards,"massey_table")
page_massey = html.Div([
    html.H1("Search Massey Solutions and Analysis"),
    html.P("Search for a Massey Card with filtered fields (case sensitive). Select a row by clicking. Results will be shown below the table."),
    massey_table,
    html.Div(id="output")
    ])

colley_table = pyrplib.style.get_standard_data_table(df_colley_cards,"colley_table")
page_colley = html.Div([
    html.H1("Search Colley Solutions and Analysis"),
    html.P("Search for a Colley Card with filtered fields (case sensitive). Select a row by clicking. Results will be shown below the table."),
    colley_table,
    html.Div(id="output")
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
                "The pathname {pathname} was not recognised...".format(pathname))
        ]
    )

# components for all pages
content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return page_datasets
    elif pathname == "/processed":
        return page_processed
    elif pathname == "/lop":
        return page_lop
    elif pathname == "/hillside":
        return page_hillside
    elif pathname == "/massey":
        return page_massey
    elif pathname == "/colley":
        return page_colley
    # if the user tries to reach a different page, return a 404 message
    return get_404(pathname)

if __name__ == "__main__":
    app.run_server(port=8888)
