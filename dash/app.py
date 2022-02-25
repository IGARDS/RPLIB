from matplotlib.font_manager import is_opentype_cff_font
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
import diskcache
import zipfile
import tempfile
import importlib

import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.long_callback import DiskcacheLongCallbackManager
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
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)


import os
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
    ],
    style=SIDEBAR_STYLE,
)

UNPROCESSED_TABLE_ID = "datasets_table"
UNPROCESSED_TABLE_DOWNLOAD_ALL_ID = "datasets_download_all"
UNPROCESSED_TABLE_DOWNLOAD_ALL_BUTTON_ID = "datasets_download_all_button"
UNPROCESSED_TABLE_DOWNLOAD_PROGRESS_ID = "datasets_download_progress"
UNPROCESSED_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID = "datasets_download_progress_collapse"
PROCESSED_TABLE_ID = "processed_table"
PROCESSED_TABLE_DOWNLOAD_ALL_ID = "processed_download_all"
PROCESSED_TABLE_DOWNLOAD_ALL_BUTTON_ID = "processed_download_all_button"
PROCESSED_TABLE_DOWNLOAD_PROGRESS_ID = "processed_download_progress"
PROCESSED_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID = "processed_download_progress_collapse"
LOP_TABLE_ID = "lop_table"
LOP_TABLE_DOWNLOAD_ALL_ID = "lop_download_all"
LOP_TABLE_DOWNLOAD_ALL_BUTTON_ID = "lop_download_all_button"
LOP_TABLE_DOWNLOAD_PROGRESS_ID = "lop_download_progress"
LOP_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID = "lop_download_progress_collapse"
HILLSIDE_TABLE_ID = "hillside_table"
HILLSIDE_TABLE_DOWNLOAD_ALL_ID = "hillside_download_all"
HILLSIDE_TABLE_DOWNLOAD_ALL_BUTTON_ID = "hillside_download_all_button"
HILLSIDE_TABLE_DOWNLOAD_PROGRESS_ID = "hillside_download_progress"
HILLSIDE_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID = "hillside_download_progress_collapse"
MASSEY_TABLE_ID = "massey_table"
MASSEY_TABLE_DOWNLOAD_ALL_ID = "massey_download_all"
MASSEY_TABLE_DOWNLOAD_ALL_BUTTON_ID = "massey_download_all_button"
MASSEY_TABLE_DOWNLOAD_PROGRESS_ID = "massey_download_progress"
MASSEY_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID = "massey_download_progress_collapse"
COLLEY_TABLE_ID = "colley_table"
COLLEY_TABLE_DOWNLOAD_ALL_ID = "colley_download_all"
COLLEY_TABLE_DOWNLOAD_ALL_BUTTON_ID = "colley_download_all_button"
COLLEY_TABLE_DOWNLOAD_PROGRESS_ID = "colley_download_progress"
COLLEY_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID = "colley_download_progress_collapse"

def get_datasets(config):
    df = config.datasets_df.copy()
    
    def process(links):
        try:
            if type(links) != list:
                links = [links]
            res = ", ".join(["[%s](%s)"%(link.split("/")[-1],link) for link in links])
            return res
        except:
            return "Could not process. Check data."

    df['Download links'] = df['Download links'].apply(process)
    df = df.drop('Loader',axis=1).drop('Description',axis=1)
    
    df = df.sort_values(by='Dataset Name')
    
    return df

def get_processed(config):
    datasets_df = df = config.datasets_df.set_index('Dataset ID')
    df = config.processed_datasets_df.copy()
            
    def process(row):
        entry = pd.Series(index=['Dataset ID','Source Dataset ID','Source Dataset Name','Short Type','Type','Command','Size','Download'])
        link = row['Link']
        entry['Dataset ID'] = row['Dataset ID']
        try:
            if row['Type'] == "D":
                d = pyrplib.dataset.ProcessedD.from_json(link).load()
            elif row['Type'] == "Games":
                d = pyrplib.dataset.ProcessedGames.from_json(link).load()
            entry.loc['Source Dataset ID'] = d.source_dataset_id
            entry.loc['Source Dataset Name'] = datasets_df.loc[d.source_dataset_id,"Dataset Name"]
            entry.loc['Dataset ID'] = d.dataset_id
            entry.loc['Short Type'] = d.short_type
            entry.loc['Type'] = d.type
            entry.loc['Command'] = d.command
            entry.loc['Size'] = d.size_str()
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
    elif method == Method.MASSEY:
        df = config.massey_cards_df.copy()
    elif method == Method.COLLEY:
        df = config.colley_cards_df.copy()
    else:
        raise ValueError('No valid card was requested from options: lop, hillside, massey, or colley')
        
    def process(row):
        if method == Method.LOP or method == Method.HILLSIDE:
            entry = pd.Series(index=['Dataset ID','Unprocessed Dataset Name','Shape of D','Objective','Found Solutions','Download'])
        elif method == Method.MASSEY or method == Method.COLLEY:
            entry = pd.Series(index=['Dataset ID','Unprocessed Dataset Name','Shape of games','Length of teams','Download'])
            
        link = row['Link']
        entry['Dataset ID'] = row['Dataset ID']
        
        try:
            if method == Method.LOP or method == Method.HILLSIDE:
                if method == Method.LOP:
                    card = pyrplib.card.LOP.from_json(link)
                else:
                    card = pyrplib.card.Hillside.from_json(link)                    
                D = card.D
                entry.loc['Shape of D'] = ",".join([str(n) for n in D.shape])
                entry.loc['Objective'] = card.obj
                entry.loc['Found Solutions'] = len(card.solutions)
            elif method == Method.MASSEY or method == Method.COLLEY:
                card = pyrplib.card.SystemOfEquations.from_json(link)
                games = card.games
                teams = card.teams
                entry.loc['Shape of games'] = ",".join([str(n) for n in games.shape])
                entry.loc['Length of teams'] = len(teams)
                
            datasets_df = config.datasets_df.set_index('Dataset ID')
            processed_datasets_df = config.processed_datasets_df.set_index('Dataset ID') 
            dataset_name = datasets_df.loc[processed_datasets_df.loc[card.source_dataset_id,"Source Dataset ID"],"Dataset Name"]
            entry.loc['Unprocessed Dataset Name'] = dataset_name
            entry.loc['Dataset ID'] = card.dataset_id
            entry.loc['Download'] = "[%s](%s)"%(link.split("/")[-1],link)
        except Exception as e:
            print("Exception in get_cards:",e)
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

@app.callback(
    Output("datasets_output", "children"),
    Input(UNPROCESSED_TABLE_ID, "active_cell"),
    State(UNPROCESSED_TABLE_ID, "derived_viewport_data"),
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
    Output(UNPROCESSED_TABLE_ID, "style_data_conditional"),
    [Input(UNPROCESSED_TABLE_ID, "active_cell")]
)
def update_selected_row_color_dataset(active):
    return update_selected_row_color(active)

@app.callback(
    Output("processed_output", "children"),
    Input(PROCESSED_TABLE_ID, "active_cell"),
    State(PROCESSED_TABLE_ID, "derived_viewport_data"),
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
    Output(PROCESSED_TABLE_ID, "style_data_conditional"),
    [Input(PROCESSED_TABLE_ID, "active_cell")]
)
def update_selected_row_color_processed(active):
    return update_selected_row_color(active)

@app.callback(
    Output("lop_output", "children"),
    Input(LOP_TABLE_ID, "active_cell"),
    State(LOP_TABLE_ID, "derived_viewport_data"),
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
    Output(LOP_TABLE_ID, "style_data_conditional"),
    [Input(LOP_TABLE_ID, "active_cell")]
)
def update_selected_row_color_lop(active):
    return update_selected_row_color(active)

def get_all_download_links_from_table(table_data, download_link_attribute):
    def unprocess_link(link, row):
        start = link.rfind('](')
        if start == -1:
            print('Attempted to strip processing on an unprocessed link')
            return link
        return {'filename' : str(row['Dataset ID'])+'_'+link[1:start], 'link' : link[start+2:-1]}

    unprocessed_links = []
    for dataset in range(len(table_data)):
        for link in table_data[dataset][download_link_attribute].split(', '):
            unprocessed_links.append(unprocess_link(link, table_data[dataset]))
    filenames = {}
    # filenames in the table can be the same--prepend increasing number
    for link in unprocessed_links:
        cur_filename = link['filename']
        if cur_filename in filenames:
            link['filename'] = str(filenames[cur_filename]) + '_' + cur_filename
            filenames[cur_filename] += 1
        else:
            filenames[cur_filename] = 1
    return unprocessed_links

def download_and_or_get_files(data, link_att_name, zipfilename, set_progress=None):
    mf = io.BytesIO()
    download_links = get_all_download_links_from_table(data, link_att_name)
    if set_progress:
        total = len(download_links)
        set_progress((str(0), str(total)))
    with zipfile.ZipFile(mf, mode="w",compression=zipfile.ZIP_DEFLATED) as zf:
        for i in range(len(download_links)):
            filename = download_links[i]['filename']
            if filename not in zf.namelist():
                link = download_links[i]['link']
                if os.path.exists(link):
                    zf.write(link, arcname=filename)
                else:
                    try:
                        file_data = requests.get(link).text
                        zf.writestr(filename, file_data)
                    except requests.ConnectionError as exception:
                        print(f"The file {filename} at {link} could not be found: {str(exception)}")
                if set_progress:
                    set_progress((str(i + 1), str(total)))
    # saves zip file in the machine dependent tempfile location 
    # creates RPLib dir if not present in temp dir location
    machine_temp_dir = tempfile.gettempdir()
    if not os.path.exists(machine_temp_dir+"/"+"RPLIB"):
        os.mkdir(machine_temp_dir+"/"+"RPLIB")
    temp_directory_file = machine_temp_dir + "/" + "RPLIB/" + zipfilename
    with open(temp_directory_file, "wb") as f:
        f.write(mf.getvalue())
        return temp_directory_file

def collapse_progress_download_logic(n_clicks, progress_val, progress_max, is_open):
    if n_clicks:
        # the progress becomes undefined when finished
        if progress_val is None or progress_max is None:
            return False
        return True
    else:
        return is_open

@app.long_callback(
    output=Output(UNPROCESSED_TABLE_DOWNLOAD_ALL_ID, "data"),
    inputs=(Input(UNPROCESSED_TABLE_DOWNLOAD_ALL_BUTTON_ID, "n_clicks"),
            State(UNPROCESSED_TABLE_ID, "derived_virtual_data")),
    progress=[Output(UNPROCESSED_TABLE_DOWNLOAD_PROGRESS_ID, "value"), 
              Output(UNPROCESSED_TABLE_DOWNLOAD_PROGRESS_ID, "max")],
)
def download_all_files_unprocessed(set_progress, n_clicks, data):
    if n_clicks != None:
        suggested_zipfilename = "unprocessed.zip"
        path_to_local_zipfile = download_and_or_get_files(data, "Download links", 
                                                          suggested_zipfilename, set_progress)
        return dcc.send_file(path_to_local_zipfile)

@app.callback(
    Output(UNPROCESSED_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID, "is_open"),
    Input(UNPROCESSED_TABLE_DOWNLOAD_ALL_BUTTON_ID, "n_clicks"),
    Input(UNPROCESSED_TABLE_DOWNLOAD_PROGRESS_ID, "value"),
    Input(UNPROCESSED_TABLE_DOWNLOAD_PROGRESS_ID, "max"),
    State(UNPROCESSED_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID, "is_open")
)
def download_all_files_unprocessed_progress_bar_display(n_clicks, progress_val, progress_max, is_open):
    return collapse_progress_download_logic(n_clicks, progress_val, progress_max, is_open)

@app.long_callback(
    output=Output(PROCESSED_TABLE_DOWNLOAD_ALL_ID, "data"),
    inputs=(Input(PROCESSED_TABLE_DOWNLOAD_ALL_BUTTON_ID, "n_clicks"),
            State(PROCESSED_TABLE_ID, "derived_virtual_data")),
    progress=[Output(PROCESSED_TABLE_DOWNLOAD_PROGRESS_ID, "value"), 
              Output(PROCESSED_TABLE_DOWNLOAD_PROGRESS_ID, "max")],
)
def download_all_files_processed(set_progress, n_clicks, data):
    if n_clicks != None:
        suggested_zipfilename = "processed.zip"
        path_to_local_zipfile = download_and_or_get_files(data, "Download", 
                                                          suggested_zipfilename, set_progress)
        return dcc.send_file(path_to_local_zipfile)

@app.callback(
    Output(PROCESSED_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID, "is_open"),
    Input(PROCESSED_TABLE_DOWNLOAD_ALL_BUTTON_ID, "n_clicks"),
    Input(PROCESSED_TABLE_DOWNLOAD_PROGRESS_ID, "value"),
    Input(PROCESSED_TABLE_DOWNLOAD_PROGRESS_ID, "max"),
    State(PROCESSED_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID, "is_open")
)
def download_all_files_processed_progress_bar_display(n_clicks, progress_val, progress_max, is_open):
    return collapse_progress_download_logic(n_clicks, progress_val, progress_max, is_open)

@app.long_callback(
    output=Output(LOP_TABLE_DOWNLOAD_ALL_ID, "data"),
    inputs=(Input(LOP_TABLE_DOWNLOAD_ALL_BUTTON_ID, "n_clicks"),
            State(LOP_TABLE_ID, "derived_virtual_data")),
    progress=[Output(LOP_TABLE_DOWNLOAD_PROGRESS_ID, "value"), 
              Output(LOP_TABLE_DOWNLOAD_PROGRESS_ID, "max")],
)
def download_all_files_lop(set_progress, n_clicks, data):
    if n_clicks != None:
        suggested_zipfilename = "lop.zip"
        path_to_local_zipfile = download_and_or_get_files(data, "Download", 
                                                          suggested_zipfilename, set_progress)
        return dcc.send_file(path_to_local_zipfile)

@app.callback(
    Output(LOP_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID, "is_open"),
    Input(LOP_TABLE_DOWNLOAD_ALL_BUTTON_ID, "n_clicks"),
    Input(LOP_TABLE_DOWNLOAD_PROGRESS_ID, "value"),
    Input(LOP_TABLE_DOWNLOAD_PROGRESS_ID, "max"),
    State(LOP_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID, "is_open")
)
def download_all_files_lop_progress_bar_display(n_clicks, progress_val, progress_max, is_open):
    return collapse_progress_download_logic(n_clicks, progress_val, progress_max, is_open)

@app.long_callback(
    output=Output(HILLSIDE_TABLE_DOWNLOAD_ALL_ID, "data"),
    inputs=(Input(HILLSIDE_TABLE_DOWNLOAD_ALL_BUTTON_ID, "n_clicks"),
            State(HILLSIDE_TABLE_ID, "derived_virtual_data")),
    progress=[Output(HILLSIDE_TABLE_DOWNLOAD_PROGRESS_ID, "value"), 
              Output(HILLSIDE_TABLE_DOWNLOAD_PROGRESS_ID, "max")],
    prevent_initial_call=True,
)
def download_all_files_hillside(set_progress, n_clicks, data):
    if n_clicks != None:
        suggested_zipfilename = "hillside.zip"
        path_to_local_zipfile = download_and_or_get_files(data, "Download", 
                                                          suggested_zipfilename, set_progress)
        return dcc.send_file(path_to_local_zipfile)
    else:
        return None

@app.callback(
    Output(HILLSIDE_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID, "is_open"),
    Input(HILLSIDE_TABLE_DOWNLOAD_ALL_BUTTON_ID, "n_clicks"),
    Input(HILLSIDE_TABLE_DOWNLOAD_PROGRESS_ID, "value"),
    Input(HILLSIDE_TABLE_DOWNLOAD_PROGRESS_ID, "max"),
    State(HILLSIDE_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID, "is_open"),
    prevent_initial_call=True,
)
def download_all_files_hillside_progress_bar_display(n_clicks, progress_val, progress_max, is_open):
    return collapse_progress_download_logic(n_clicks, progress_val, progress_max, is_open)

@app.long_callback(
    output=Output(COLLEY_TABLE_DOWNLOAD_ALL_ID, "data"),
    inputs=(Input(COLLEY_TABLE_DOWNLOAD_ALL_BUTTON_ID, "n_clicks"),
            State(COLLEY_TABLE_ID, "derived_virtual_data")),
    progress=[Output(COLLEY_TABLE_DOWNLOAD_PROGRESS_ID, "value"), 
              Output(COLLEY_TABLE_DOWNLOAD_PROGRESS_ID, "max")],
    prevent_initial_call=True,
)
def download_all_files_colley(set_progress, n_clicks, data):
    if n_clicks != None:
        suggested_zipfilename = "colley.zip"
        path_to_local_zipfile = download_and_or_get_files(data, "Download", 
                                                          suggested_zipfilename, set_progress)
        return dcc.send_file(path_to_local_zipfile)

@app.callback(
    Output(COLLEY_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID, "is_open"),
    Input(COLLEY_TABLE_DOWNLOAD_ALL_BUTTON_ID, "n_clicks"),
    Input(COLLEY_TABLE_DOWNLOAD_PROGRESS_ID, "value"),
    Input(COLLEY_TABLE_DOWNLOAD_PROGRESS_ID, "max"),
    State(COLLEY_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID, "is_open"),
    prevent_initial_call=True,
)
def download_all_files_colley_progress_bar_display(n_clicks, progress_val, progress_max, is_open):
    return collapse_progress_download_logic(n_clicks, progress_val, progress_max, is_open)

@app.long_callback(
    output=Output(MASSEY_TABLE_DOWNLOAD_ALL_ID, "data"),
    inputs=(Input(MASSEY_TABLE_DOWNLOAD_ALL_BUTTON_ID, "n_clicks"),
            State(MASSEY_TABLE_ID, "derived_virtual_data")),
    progress=[Output(MASSEY_TABLE_DOWNLOAD_PROGRESS_ID, "value"), 
              Output(MASSEY_TABLE_DOWNLOAD_PROGRESS_ID, "max")],
    prevent_initial_call=True,
)
def download_all_files_massey(set_progress, n_clicks, data):
    if n_clicks != None:
        suggested_zipfilename = "massey.zip"
        path_to_local_zipfile = download_and_or_get_files(data, "Download", 
                                                          suggested_zipfilename, set_progress)
        return dcc.send_file(path_to_local_zipfile)
    else:
        return None

@app.callback(
    Output(MASSEY_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID, "is_open"),
    Input(MASSEY_TABLE_DOWNLOAD_ALL_BUTTON_ID, "n_clicks"),
    Input(MASSEY_TABLE_DOWNLOAD_PROGRESS_ID, "value"),
    Input(MASSEY_TABLE_DOWNLOAD_PROGRESS_ID, "max"),
    State(MASSEY_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID, "is_open"),
    prevent_initial_call=True,
)
def download_all_files_massey_progress_bar_display(n_clicks, progress_val, progress_max, is_open):
    return collapse_progress_download_logic(n_clicks, progress_val, progress_max, is_open)

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
@app.callback(
    Output("massey_output", "children"),
    Input("massey_table", "active_cell"),
    State("massey_table", "derived_viewport_data"),
)
def cell_clicked_massey(cell,data):
    if cell is None:
        return dash.no_update
    row,col = cell["row"],cell["column_id"]
    selected = data[row][col]
    if selected is not None:
        dataset_id = data[row]['Dataset ID']
        link = config.massey_cards_df.set_index('Dataset ID').loc[dataset_id,"Link"]
        options = config.massey_cards_df.set_index('Dataset ID').loc[dataset_id,"Options"]
        if type(options) == str:
            options = json.loads(options)
            options_str = json.dumps(options,indent=2)
        else:
            options_str = "None"
        obj = pyrplib.card.SystemOfEquations.from_json(link)
        
        processed_datasets_df = config.processed_datasets_df.set_index('Dataset ID') 
        datasets_df = config.datasets_df.set_index('Dataset ID') 
        description = datasets_df.loc[processed_datasets_df.loc[obj.source_dataset_id,"Source Dataset ID"],"Description"]
        dataset_name = datasets_df.loc[processed_datasets_df.loc[obj.source_dataset_id,"Source Dataset ID"],"Dataset Name"]
        
        contents = [html.Br(),html.H2("Source Dataset Name"),html.P(dataset_name),html.H2("Description"),html.P(description),html.H2("Options"),html.Pre(options_str)]+obj.view()
        return html.Div(contents)
    else:
        return dash.no_update  
    
@app.callback(
    Output("massey_table", "style_data_conditional"),
    [Input("massey_table", "active_cell")]
)
def update_selected_row_color_massey(active):
    return update_selected_row_color(active)

@app.callback(
    Output("colley_output", "children"),
    Input("colley_table", "active_cell"),
    State("colley_table", "derived_viewport_data"),
)
def cell_clicked_colley(cell,data):
    if cell is None:
        return dash.no_update
    row,col = cell["row"],cell["column_id"]
    selected = data[row][col]
    if selected is not None:
        dataset_id = data[row]['Dataset ID']
        link = config.colley_cards_df.set_index('Dataset ID').loc[dataset_id,"Link"]
        options = config.colley_cards_df.set_index('Dataset ID').loc[dataset_id,"Options"]
        if type(options) == str:
            options = json.loads(options)
            options_str = json.dumps(options,indent=2)
        else:
            options_str = "None"
        obj = pyrplib.card.SystemOfEquations.from_json(link)
        
        processed_datasets_df = config.processed_datasets_df.set_index('Dataset ID') 
        datasets_df = config.datasets_df.set_index('Dataset ID') 
        description = datasets_df.loc[processed_datasets_df.loc[obj.source_dataset_id,"Source Dataset ID"],"Description"]
        dataset_name = datasets_df.loc[processed_datasets_df.loc[obj.source_dataset_id,"Source Dataset ID"],"Dataset Name"]
        
        contents = [html.Br(),html.H2("Source Dataset Name"),html.P(dataset_name),html.H2("Description"),html.P(description),html.H2("Options"),html.Pre(options_str)]+obj.view()
        return html.Div(contents)
    else:
        return dash.no_update  
    
@app.callback(
    Output("colley_table", "style_data_conditional"),
    [Input("colley_table", "active_cell")]
)
def update_selected_row_color_colley(active):
    return update_selected_row_color(active)

@app.callback(
    Output("hillside_output", "children"),
    Input(HILLSIDE_TABLE_ID, "active_cell"),
    State(HILLSIDE_TABLE_ID, "derived_viewport_data"),
)
def cell_clicked_hillside(cell,data):
    if cell is None:
        return dash.no_update
    row,col = cell["row"],cell["column_id"]
    selected = data[row][col]
    if selected is not None:
        dataset_id = data[row]['Dataset ID']
        link = config.hillside_cards_df.set_index('Dataset ID').loc[dataset_id,"Link"]
        options = config.hillside_cards_df.set_index('Dataset ID').loc[dataset_id,"Options"]
        if type(options) == str:
            options = json.loads(options)
            options_str = json.dumps(options,indent=2)
        else:
            options_str = "None"
        obj = pyrplib.card.Hillside.from_json(link)
        
        processed_datasets_df = config.processed_datasets_df.set_index('Dataset ID') 
        datasets_df = config.datasets_df.set_index('Dataset ID') 
        description = datasets_df.loc[processed_datasets_df.loc[obj.source_dataset_id,"Source Dataset ID"],"Description"]
        dataset_name = datasets_df.loc[processed_datasets_df.loc[obj.source_dataset_id,"Source Dataset ID"],"Dataset Name"]
        
        contents = [html.Br(),html.H2("Source Dataset Name"),html.P(dataset_name),html.H2("Description"),html.P(description),html.H2("Options"),html.Pre(options_str)]+obj.view()
        return html.Div(contents)
    else:
        return dash.no_update  
    
@app.callback(
    Output(HILLSIDE_TABLE_ID, "style_data_conditional"),
    [Input(HILLSIDE_TABLE_ID, "active_cell")]
)
def update_selected_row_color_hillside(active):
    return update_selected_row_color(active)


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
@app.callback(
    Output("lop_help_show", "is_open"),
    Input("lop_help_button", "n_clicks"),
    State("lop_help_show", "is_open"),
    prevent_initial_call=True,
)
def lop_help_button(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open
    
lop_help_button = \
    pyrplib.style.get_standard_help_button("lop_help_button", "lop_help_show", "help text")
page_lop = html.Div([
    html.H1("Search LOP Solutions and Analysis (i.e., LOP cards)"),
    html.P("Search for LOP card with filtered fields (case sensitive). Select a row by clicking. Results will be shown below the table."),
    lop_download_button,
    lop_help_button,
    lop_table,
    html.Br(),
    html.H2("Selected content will appear below"),
    html.Div(id="lop_output")
])

hillside_table = pyrplib.style.get_standard_data_table(df_hillside_cards, HILLSIDE_TABLE_ID)
hillside_download_button = \
    pyrplib.style.get_standard_download_all_button(HILLSIDE_TABLE_DOWNLOAD_ALL_BUTTON_ID, 
                                                   HILLSIDE_TABLE_DOWNLOAD_ALL_ID,
                                                   HILLSIDE_TABLE_DOWNLOAD_PROGRESS_ID,
                                                   HILLSIDE_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID)
page_hillside = html.Div([
    html.H1("Search Hillside Solutions and Analysis"),
    html.P("Search for a Hillside Card with filtered fields (case sensitive). Select a row by clicking. Results will be shown below the table."),
    hillside_download_button,
    hillside_table,
    html.Br(),
    html.H2("Selected content will appear below"),
    html.Div(id="hillside_output")
    ])

massey_table = pyrplib.style.get_standard_data_table(df_massey_cards, MASSEY_TABLE_ID)
massey_download_button = \
    pyrplib.style.get_standard_download_all_button(MASSEY_TABLE_DOWNLOAD_ALL_BUTTON_ID, 
                                                   MASSEY_TABLE_DOWNLOAD_ALL_ID,
                                                   MASSEY_TABLE_DOWNLOAD_PROGRESS_ID,
                                                   MASSEY_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID)
page_massey = html.Div([
    html.H1("Search Massey Solutions and Analysis"),
    html.P("Search for a Massey Card with filtered fields (case sensitive). Select a row by clicking. Results will be shown below the table."),
    massey_download_button,
    massey_table,
    html.Br(),
    html.H2("Selected content will appear below"),
    html.Div(id="massey_output")
    ])

colley_table = pyrplib.style.get_standard_data_table(df_colley_cards, COLLEY_TABLE_ID)
colley_download_button = \
    pyrplib.style.get_standard_download_all_button(COLLEY_TABLE_DOWNLOAD_ALL_BUTTON_ID, 
                                                   COLLEY_TABLE_DOWNLOAD_ALL_ID,
                                                   COLLEY_TABLE_DOWNLOAD_PROGRESS_ID,
                                                   COLLEY_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID)
page_colley = html.Div([
    html.H1("Search Colley Solutions and Analysis"),
    html.P("Search for a Colley Card with filtered fields (case sensitive). Select a row by clicking. Results will be shown below the table."),
    colley_download_button,
    colley_table,
    html.Div(id="colley_output")
    ])

def get_download_local_file_button(pathname):
    button_text = "Download: " + pathname.split('/')[-1]
    fake_button = html.Button(button_text, key=pathname, id="btn-download-file")
    return html.Div([
        fake_button,
        dcc.Download(id="download-file")
    ])

@app.callback(
    Output("download-file", "data"),
    [Input("btn-download-file", "key")],
)
def download_local_file(pathname):
    return dcc.send_file(pathname)


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
    if pathname == "BASE_PATH":
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

if __name__ == "__main__":
    app.run_server(port=8888)
