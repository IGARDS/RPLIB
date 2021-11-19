import requests
import io
import sys
import traceback

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import numpy as np
import altair as alt
from dash.dependencies import Input, Output, State
import urllib

from pathlib import Path
home = str(Path.home())
sys.path.insert(0,"%s"%home)

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

def get_style():
    return {'style_header': {
        'backgroundColor': 'white',
        'fontWeight': 'bold',
        "border": "1px solid white",
    },
    'style_cell': {
        'whiteSpace': 'normal',
        'height': 'auto',
        'textAlign': 'left'
    },
    'filter_action': 'native',
    'style_data': {
        "backgroundColor": '#E3F2FD',
        "border-bottom": "1px solid #90CAF9",
        "border-top": "1px solid #90CAF9",
        "border-left": "1px solid #E3F2FD",
        "border-right": "1px solid #E3F2FD"},
    'style_data_conditional': [
    {
        "if": {"state": "selected"},
        "backgroundColor": '#E3F2FD',
        "border-bottom": "1px solid #90CAF9",
        "border-top": "1px solid #90CAF9",
        "border-left": "1px solid #E3F2FD",
        "border-right": "1px solid #E3F2FD",
    }]
    }
                

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
        except Exception as e:
            print("Exception in get_Ds:",e)
            print(traceback.format_exc())
        return entry

    Ds = df['Link'].apply(process)
    
    return Ds

def get_solution_cards(algorithm):
    if algorithm == 'lop':
        link = "https://raw.githubusercontent.com/IGARDS/RPLib/master/data/dataset_tool_lop_cards.tsv"
    elif algorithm == 'hillside':
        link = "https://raw.githubusercontent.com/IGARDS/RPLib/master/data/dataset_tool_hillside_cards.tsv"
    elif algorithm == 'colley':
        link = "https://raw.githubusercontent.com/IGARDS/RPLib/master/data/dataset_tool_colley_cards.tsv"
    elif algorithm == 'massey':
        link = "https://raw.githubusercontent.com/IGARDS/RPLib/master/data/dataset_tool_massey_cards.tsv"

    # throws a urllib.error.HTTPError error if link can't be found. This is caught in the render function.
    df = pd.read_csv(link, sep='\t')

    def process(link):
        d = requests.get(link).json()
        entry = pd.Series(index=['Dataset ID','Shape of D','Objective','Number of Solutions','Generate Report','Download'])
        try:
            entry.loc['Dataset ID'] = d['dataset_id']
            D = pd.DataFrame(d['D'])
            entry.loc['Shape of D'] = ",".join([str(n) for n in D.shape])
            entry.loc['Objective'] = d['obj']
            entry.loc['Number of Solutions'] = len(d['solutions'])
            entry.loc['Generate Report'] = 'Generate'
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

def get_dataset_table():
    return dash_table.DataTable(
    id="dataset_table",
    columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df_datasets.columns],
    data=df_datasets.to_dict("records"),
    is_focused=True,
    **get_style()
    )

def get_D_table():
    return dash_table.DataTable(
    id="D_table",
    columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df_Ds.columns],
    data=df_Ds.to_dict("records"),
    is_focused=True,
    **get_style()
    )

def get_lop_table():
    df_lop_cards, _ = get_solution_cards('lop')
    return dash_table.DataTable(
    id="lop_table",
    columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df_lop_cards.columns],
    data=df_lop_cards.to_dict("records"),
    is_focused=True,
    **get_style()
    )

def get_hillside_table():
    df_hillside_cards, _ = get_solution_cards('hillside')
    return dash_table.DataTable(
    id="hillside_table",
    columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df_hillside_cards.columns],
    data=df_hillside_cards.to_dict("records"),
    is_focused=True,
    **get_style()
    )

def get_massey_table():
    df_massey_cards, _ = get_solution_cards('massey')
    return dash_table.DataTable(
    id="massey_table",
    columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df_massey_cards.columns],
    data=df_massey_cards.to_dict("records"),
    is_focused=True,
    **get_style()
    )

def get_colley_table():
    df_colley_cards, _ = get_solution_cards('colley')
    return dash_table.DataTable(
    id="colley_table",
    columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df_colley_cards.columns],
    data=df_colley_cards.to_dict("records"),
    is_focused=True,
    **get_style()
    )

def get_page_datasets():
    return html.Div([
    html.H1("Search datasets"),
    html.P("Try searching for a dataset with filtered fields. Select a row to navigate to the raw dataset."),
    get_dataset_table(),
    html.Div(id="output")
    ])

def get_page_Ds():
    return html.Div([
    html.H1("Search D matrices"),
    html.P("Try searching for a D matrix with filtered fields. Select a row to navigate to the raw dataset."),
    get_D_table(),
    html.Div(id="output")
    ])

def get_page_lop():
    return html.Div([
    html.H1("Search LOP Solutions and Analysis (i.e., LOP cards)"),
    html.P("Try searching for a LOP card with filtered fields. Select a row to navigate to the raw dataset."),
    get_lop_table(),
    html.Div(id="output")
    ])

def get_page_hillside():
    return html.Div([
    html.H1("Search Hillside Solutions and Analysis"),
    html.P("This is currently empty."),
    html.Div(id="output")
    ])

def get_page_massey():
    return html.Div([
    html.H1("Search Massey Solutions and Analysis"),
    html.P("This is currently empty."),
    html.Div(id="output")
]   )

def get_page_colley():
    return html.Div([
    html.H1("Search Colley Solutions and Analysis"),
    html.P("This is currently empty."),
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

def generate_lop_report(d, link, show_solutions=True, show_xstar=True, show_spider=True):
    selected = []
    # 'View Two Solutions':
    if show_solutions:
        selected.append(html.H3("Two Solutions"))
        df_solutions = pd.DataFrame(d['solutions'])
        selected.append(dash_table.DataTable(
            id="solutions_table", # same id for the table in html - causes the original table to get overriden
            columns=[{"name": i, "id": i, 'presentation': 'markdown'} for i in df_solutions.columns],
            data=df_solutions.to_dict("records"),
            is_focused=True,
            **get_style()
        ))
    
    if show_xstar or show_spider:
        lop_card = pyrplib.base.LOPCard.from_json(link)
        plot_html = io.StringIO()
        D = pd.DataFrame(lop_card.D)
    # 'Red/Green plot':
    if show_xstar:
        selected.append(html.H3("Red/Green plot"))
        x=pd.DataFrame(lop_card.centroid_x,index=D.index,columns=D.columns)
        xstar_g,scores,ordered_xstar=pyrankability.plot.show_single_xstar(x)
        xstar_g.save(plot_html, 'html')

        selected.append(html.Iframe(
            id='xstar_plot',
            height='500',
            width='1000',
            sandbox='allow-scripts',
            srcDoc=plot_html.getvalue(),
            style={'border-width': '0px'}
        ))
    # 'Nearest/Farthest Centoid Plot':
    if show_spider:
        selected.append(html.H3("Nearest/Farthest Centroid Plot"))
        outlier_solution = pd.Series(lop_card.outlier_solution,
                                        index=D.index[lop_card.outlier_solution],
                                        name="Farthest from Centroid")
        centroid_solution = pd.Series(lop_card.centroid_solution,
                                        index=D.index[lop_card.centroid_solution],
                                        name="Closest to Centroid")
        spider_g = pyrankability.plot.spider3(outlier_solution,centroid_solution)
        spider_g.save(plot_html, 'html')

        selected.append(html.Iframe(
            id='spider_plot',
            height='500',
            width='1000',
            sandbox='allow-scripts',
            srcDoc=plot_html.getvalue(),
            style={'border-width': '0px'}
        ))
    return selected

@app.callback(
    Output("output", "children"),
    Input("lop_table", "active_cell"),
    State("lop_table", "derived_viewport_data"),
)
def cell_clicked(cell, data):
    if cell:
        row,col = cell["row"],cell["column_id"]
        link = data[row]['Link']
        d = requests.get(link).json()
        selected = data[row][col]

        if col == 'Generate Report':
            selected = generate_lop_report(d, link, show_solutions=True, show_xstar=False, show_spider=False)
            contents = [html.Br(),html.H2("Dataset Report"), *selected]
        else:
            contents = [html.Br(),html.H2("No Content Selected"), None]

        return html.Div(contents)
    else:
        return dash.no_update

# components for all pages
content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])
# could be used to save the get_page functions return
pages = {'page_datasets': None, 'page_Ds': None, 'page_lop': None, 'page_hillside': None, 'page_massey': None, 'page_colley': None}

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    try:
        if pathname == "/":
            return get_page_datasets()
        elif pathname == "/D":
            return get_page_Ds()
        elif pathname == "/lop":
            return get_page_lop()
        elif pathname == "/hillside":
            return get_page_hillside()
        elif pathname == "/massey":
            return get_page_massey()
        elif pathname == "/colley":
            return get_page_colley()
    except urllib.error.HTTPError:
        # get solution cards returns this error when no data can be found for the solution page
        return get_blank_page(pathname[1:])
    # if the user tries to reach a different page, return a 404 message
    return get_404(pathname)

if __name__ == "__main__":
    app.run_server(port=8888)
