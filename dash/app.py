import requests
import io
import sys
import traceback
#from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import numpy as np
import altair as alt
from dash.dependencies import Input, Output, State

from pathlib import Path
home = str(Path.home())
#sys.path.insert(0,"%s"%home) # this python path only works if the user puts the directory within their home
sys.path.insert(0, "../../") # this one only works if the user follows the advice to put both RPlib and ranking_toolbox within its own folder

import RPLib.pyrplib as pyrplib
import ranking_toolbox.pyrankability as pyrankability

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# the style arguments for the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position to the right of the sidebar
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("RP Lib", className="display-4"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Search Datasets", href="/", active="exact"),
                dbc.NavLink("Search D Matrices", href="/D", active="exact"),
                dbc.NavLink("Search LOP", href="/lop", active="exact"),
                dbc.NavLink("Search Hillside", href="/hillside", active="exact"),
                dbc.NavLink("Search Colley", href="/colley", active="exact"),
                dbc.NavLink("Search Massey", href="/massey", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

# components for 'Search datasets' page
#df = pd.read_csv(
#    "https://raw.githubusercontent.com/IGARDS/RPLib/master/data/dataset_tool_datasets.tsv",sep='\t')

def get_datasets():
    df = pd.read_csv(
        "https://raw.githubusercontent.com/IGARDS/RPLib/master/data/dataset_tool_datasets.tsv",sep='\t')

    column_info = df.iloc[0,:]
    df = df.iloc[1:]
    
    df2 = df.copy()
    def process(links):
        try:
            if type(links) != list:
                links = [links]
            #res = ",".join([link.split("/")[-1] for link in links])
            res = ", ".join(["[%s](%s)"%(link.split("/")[-1],link) for link in links])
            return res
        except:
            return "Could not process. Check data."
        
    df['Download links'] = df['Download links'].str.split(",")
    df['Data provenance'] = df['Data provenance'].str.split(",")

    df2['Data provenance'] = df2['Data provenance'].str.split(",").apply(process)
    df2['Download links'] = df2['Download links'].str.split(",").apply(process)
    
    return df2,df

def get_Ds(df_datasets,df_datasets_raw):
    df = pd.read_csv("https://raw.githubusercontent.com/IGARDS/RPLib/master/data/dataset_tool_Ds.tsv",sep='\t')
            
    def process(link):
        d = requests.get(link).json()
        D = pd.DataFrame(d["D"])
        entry = pd.Series(index=['Source Dataset ID','Dataset ID','D Type','Command','Shape D','Download'])
        try:
            entry.loc['Source Dataset ID'] = d['source_dataset_id']
            entry.loc['Dataset ID'] = d['dataset_id']
            entry.loc['D Type'] = d['D_type']
            entry.loc['Command'] = d['command']
            entry.loc['Shape D'] = D.shape
            entry.loc['Download'] = "[%s](%s)"%(link.split("/")[-1],link)
        except:
            print("Exception in get_Ds:",e)
            print(traceback.format_exc())
        return entry

    Ds = df['Link'].apply(process)
    
    return Ds

def get_lop_cards():
    df = pd.read_csv(
        "https://raw.githubusercontent.com/IGARDS/RPLib/master/data/dataset_tool_lop_cards.tsv",sep='\t')

    def process(link):
        #print(link)
        d = requests.get(link).json()
        #print(d['dataset_id'])
        #print(d.keys())
        entry = pd.Series(index=['Dataset ID','Shape of D','Objective','Number of Solutions','View Two Solutions', 'Red/Green plot','Download'])
        try:
            entry.loc['Dataset ID'] = d['dataset_id']
            D = pd.DataFrame(d['D'])
            entry.loc['Shape of D'] = ",".join([str(n) for n in D.shape])
            entry.loc['Objective'] = d['obj']
            entry.loc['Number of Solutions'] = len(d['solutions'])
            entry.loc['View Two Solutions'] = 'View'
            entry.loc['Red/Green plot'] = 'Generate'
            entry.loc['Nearest/Farthest Centoid Plot'] = 'Generate'
            entry.loc['Download'] = "[%s](%s)"%(link.split("/")[-1],link)
        except Exception as e:
            print("Exception in get_lop_cards:",e)
            print(traceback.format_exc())
        return entry

    cards = df['Link'].apply(process)
    df2 = cards.set_index('Dataset ID').join(df.set_index('Dataset ID')).reset_index()
        
    return df2,df

df_datasets,df_datasets_raw = get_datasets()

df_Ds = get_Ds(df_datasets,df_datasets_raw)

df_lop_cards,df_lop_cards_raw = get_lop_cards()

dataset_table = dash_table.DataTable(
    id="table",
    columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df_datasets.columns],
    data=df_datasets.to_dict("records"),
    is_focused=True,
    style_header={
        'backgroundColor': 'white',
        'fontWeight': 'bold',
        "border": "1px solid white",
    },
    style_cell={
        'whiteSpace': 'normal',
        'height': 'auto',
        'textAlign': 'left'
    },
    filter_action='native',
    style_data={
        "backgroundColor": '#E3F2FD',
        "border-bottom": "1px solid #90CAF9",
        "border-top": "1px solid #90CAF9",
        "border-left": "1px solid #E3F2FD",
        "border-right": "1px solid #E3F2FD"},
    style_data_conditional=[
        {
            "if": {"state": "selected"},
            "backgroundColor": '#E3F2FD',
            "border-bottom": "1px solid #90CAF9",
            "border-top": "1px solid #90CAF9",
            "border-left": "1px solid #E3F2FD",
            "border-right": "1px solid #E3F2FD",
        }
    ]
)

D_table = dash_table.DataTable(
    id="table",
    columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df_Ds.columns],
    data=df_Ds.to_dict("records"),
    is_focused=True,
    style_header={
        'backgroundColor': 'white',
        'fontWeight': 'bold',
        "border": "1px solid white",
    },
    style_cell={
        'whiteSpace': 'normal',
        'height': 'auto',
        'textAlign': 'left'
    },
    filter_action='native',
    style_data={
        "backgroundColor": '#E3F2FD',
        "border-bottom": "1px solid #90CAF9",
        "border-top": "1px solid #90CAF9",
        "border-left": "1px solid #E3F2FD",
        "border-right": "1px solid #E3F2FD"},
    style_data_conditional=[
        {
            "if": {"state": "selected"},
            "backgroundColor": '#E3F2FD',
            "border-bottom": "1px solid #90CAF9",
            "border-top": "1px solid #90CAF9",
            "border-left": "1px solid #E3F2FD",
            "border-right": "1px solid #E3F2FD",
        }
    ]
)

lop_table = dash_table.DataTable(
    id="table",
    #dict(name='a', id='a', type='text', presentation='markdown')
    columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df_lop_cards.columns],
    data=df_lop_cards.to_dict("records"),
    is_focused=True,
    style_header={
        'backgroundColor': 'white',
        'fontWeight': 'bold',
        "border": "1px solid white",
    },
    style_cell={
        'whiteSpace': 'normal',
        'height': 'auto',
        'textAlign': 'left'
    },
    filter_action='native',
    style_data={
        "backgroundColor": '#E3F2FD',
        "border-bottom": "1px solid #90CAF9",
        "border-top": "1px solid #90CAF9",
        "border-left": "1px solid #E3F2FD",
        "border-right": "1px solid #E3F2FD"},
    style_data_conditional=[
        {
            "if": {"state": "selected"},
            "backgroundColor": '#E3F2FD',
            "border-bottom": "1px solid #90CAF9",
            "border-top": "1px solid #90CAF9",
            "border-left": "1px solid #E3F2FD",
            "border-right": "1px solid #E3F2FD",
        }
    ]
)

page_datasets = html.Div([
    html.H1("Search datasets"),
    html.P("Try searching for a dataset with filtered fields. Select a row to navigate to the raw dataset."),
    dataset_table,
    html.Div(id="output")
])

page_Ds = html.Div([
    html.H1("Search D matrices"),
    html.P("Try searching for a D matrix with filtered fields. Select a row to navigate to the raw dataset."),
    D_table,
    html.Div(id="output")
])

page_lop = html.Div([
    html.H1("Search LOP Solutions and Analysis (i.e., LOP cards)"),
    html.P("Try searching for a LOP card with filtered fields. Select a row to navigate to the raw dataset."),
    lop_table,
    html.Div(id="output")
])

page_hillside = html.Div([
    html.H1("Search Hillside Solutions and Analysis"),
    html.P("This is currently empty."),
    html.Div(id="output")
])

page_massey = html.Div([
    html.H1("Search Massey Solutions and Analysis"),
    html.P("This is currently empty."),
    html.Div(id="output")
])

page_colley = html.Div([
    html.H1("Search Colley Solutions and Analysis"),
    html.P("This is currently empty."),
    html.Div(id="output")
])


@app.callback(
    Output("output", "children"),
    Input("table", "active_cell"),
    State("table", "derived_viewport_data"),
)
def cell_clicked(cell, data):
    if cell:
        row,col = cell["row"],cell["column_id"]
        link = data[row]['Link']
        d = requests.get(link).json()
        selected = data[row][col]
        if col == 'View Two Solutions':
            df_solutions = pd.DataFrame(d['solutions'])
            selected = dash_table.DataTable(
                id="table2", # same id for the table in html - causes the original table to get overriden
                #dict(name='a', id='a', type='text', presentation='markdown')
                columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df_solutions.columns],
                data=df_solutions.to_dict("records"),
                is_focused=True,
                style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold',
                    "border": "1px solid white",
                },
                style_cell={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'textAlign': 'left'
                },
                filter_action='native',
                style_data={
                    "backgroundColor": '#E3F2FD',
                    "border-bottom": "1px solid #90CAF9",
                    "border-top": "1px solid #90CAF9",
                    "border-left": "1px solid #E3F2FD",
                    "border-right": "1px solid #E3F2FD"},
                style_data_conditional=[
                    {
                        "if": {"state": "selected"},
                        "backgroundColor": '#E3F2FD',
                        "border-bottom": "1px solid #90CAF9",
                        "border-top": "1px solid #90CAF9",
                        "border-left": "1px solid #E3F2FD",
                        "border-right": "1px solid #E3F2FD",
                    }
                ]
            )
        if col == 'Red/Green plot':
            lop_card = pyrplib.base.LOPCard.from_json(link)

            plot_html = io.StringIO()
            D = pd.DataFrame(lop_card.D)
            x=pd.DataFrame(lop_card.centroid_x,index=D.index,columns=D.columns)
            g,scores,ordered_xstar=pyrankability.plot.show_single_xstar(x)
            g.save(plot_html, 'html')

            selected = html.Iframe(
                id='plot',
                height='500',
                width='1000',
                sandbox='allow-scripts',
                srcDoc=plot_html.getvalue(),
                style={'border-width': '0px'}
            )
        if col == 'Nearest/Farthest Centoid Plot':
            lop_card = pyrplib.base.LOPCard.from_json(link)
            D = pd.DataFrame(lop_card.D)
            outlier_solution = pd.Series(lop_card.outlier_solution,
                                         index=D.index[lop_card.outlier_solution],
                                         name="Farthest from Centroid")
            centroid_solution = pd.Series(lop_card.centroid_solution,
                                          index=D.index[lop_card.centroid_solution],
                                          name="Closest to Centroid")
            g = pyrankability.plot.spider3(outlier_solution,centroid_solution)
            plot_html = io.StringIO()
            g.save(plot_html, 'html')

            selected = html.Iframe(
                id='plot',
                height='500',
                width='1000',
                sandbox='allow-scripts',
                srcDoc=plot_html.getvalue(),
                style={'border-width': '0px'}
            )

        contents = [html.Br(),html.H2("Content Selected"),selected]
        #if col is 
        #for i in range(len(links)):
        #    if i > 0:
        #        contents.append(html.Br())
        #    contents.append(html.A("View {}".format(selected[i]), href=links[i]))

        return html.Div(contents)
    else:
        return dash.no_update


# components for all pages
content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return page_datasets
    elif pathname == "/D":
        return page_Ds
    elif pathname == "/lop":
        return page_lop
    elif pathname == "/hillside":
        return page_hillside
    elif pathname == "/massey":
        return page_massey
    elif pathname == "/colley":
        return page_colley
    # if the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(
                "The pathname {pathname} was not recognised...".format(pathname))
        ]
    )


if __name__ == "__main__":
    app.run_server(port=8888)
