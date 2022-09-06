from dash import dash_table
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
from dash import html
import json

def get_datatype(dtype):
    if 'float' in dtype or 'double' in dtype or 'int' in dtype:
        return 'numeric'
    elif 'datetime' in dtype:
        return 'datetime'
    return 'text'
    
def get_filter_options(dtype):
    if 'float' in dtype or 'double' in dtype or 'int' in dtype:
        return 'sensitive'
    return 'insensitive'

def get_standard_data_table(df,id):
    """Returns a dash data table with standard configuration.
    """
    if type(df) == pd.Series:
        df = df.to_frame().reset_index()
    df = df.fillna("")

    dataset_table = dash_table.DataTable(
        id=id,
        columns=[{
            "name": i, "id": i, 'presentation': 'markdown', 
            "type": get_datatype(str(df[i].dtype)),
            "filter_options": {"case": get_filter_options(str(df[i].dtype))}
        } for i in df.columns],
        data=df.to_dict("records"),
        is_focused=True,
        style_table={
            'height': 500,
            'overflowY': 'scroll',
        },
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
        sort_action="native",
        sort_mode="multi",
        filter_action='native',
#        filter_options={ # moved this to each column because of bug with filtering
#            'case': 'sensitive' #'insensitive'
#        },
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
    return dataset_table

def get_standard_download_all_button(button_id, download_id, progress_id=None, collapse_id=None):
    """Return a standard download button.
    """
    if progress_id and collapse_id:     
        button = html.Div(
            [
                html.Div([
                    dbc.Collapse(
                        dbc.Row(
                            [
                                html.Progress(id=progress_id)
                            ]
                        ),
                        id=collapse_id,
                        is_open=False
                    ),
                    dcc.Download(id=download_id),
                ]),
                dbc.Row(
                    [
                        html.Button(id=button_id, children="Download All In Table"),
                    ]
                )
            ]
        )
    else:
        button = html.Div(
            [
                html.Div([
                    dcc.Download(id=download_id),
                ], style={'display': 'inline-block'}),
                html.Button(id=button_id, children="Download All In Table", style={'padding': "5px 15px", "borderRadius": "7px",
                                                                                   'backgroundColor': "#0c6efd",
                                                                                   'color': "white", 'border': 'none'}),
            ],
            style={'float': 'right'}
        ) 
    return button

def view_item(item,id):
    """Helper function to view a single item.
    """
    html_comps = []
    j = 0
    for index in item.index:
        html_comps.append(html.H4(index))
        d = item[index]
        if type(d) == pd.DataFrame:
            html_comps.append(get_standard_data_table(d,f"data_view_item_{j}")) 
        elif type(d) == list:
            html_comps.append(html.Pre("\n".join([str(di) for di in d])))
        elif d is None:
            html_comps.append(html.Pre("None"))            
        else:
            html_comps.append(html.Pre(d))
        j += 1
    
    return html_comps