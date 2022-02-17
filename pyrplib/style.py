from dash import dash_table
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

def get_standard_data_table(df,id):
    def get_datatypes(dtype):
        if 'float' in dtype or 'double' in dtype or 'int' in dtype:
            return 'numeric'
        elif 'datetime' in dtype:
            return 'datetime'
        return 'text'
    dataset_table = dash_table.DataTable(
        id=id,
        columns=[{"name": i, "id": i, 'presentation': 'markdown', 
                "type": get_datatypes(str(df[i].dtype))} for i in df.columns],
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
        filter_action='native',
        filter_options={
            'case': 'insensitive'
        },
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

def get_standard_download_all_button(button_id, download_id, progress_id=None):
    button = html.Div(
        [
            html.Div([
                #html.Progress(id=progress_id, style={"visibility": "hidden"}),
                dcc.Download(id=download_id),
            ]),
            dbc.Row(
                [
                    html.Button(id=button_id, children="Download All In Table"),
                ],
                justify="right"
            )
            
        ]
    ) 
    return button
