from dash.dependencies import Input, Output, State
import dash
from dash import html

import pyrankability
import pyrplib

from .identifier import *
from . import app
from . import config

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

def setup_cell_clicked_dataset():
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
        description = str(datasets_df.loc[dataset_id,'Description'])
        if selected is not None:
            unprocessed = pyrplib.dataset.load_unprocessed(dataset_id,datasets_df)
            description = description.replace("\\n","\n")
            description_html = [html.H3("Description"),html.Pre(description)]
            contents = [html.Br(),html.H2(dataset_name)] + description_html + [html.H3("Data")] + unprocessed.view()
            return html.Div(contents)
        else:
            return dash.no_update

def setup_cell_clicked_processed():
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
            processed_datasets_df = config.processed_datasets_df.set_index('Dataset ID')
            datasets_df = config.datasets_df.set_index('Dataset ID')

            link = processed_datasets_df.loc[dataset_id,"Link"]
            options = processed_datasets_df.loc[dataset_id,"Options"]
            if type(options) == str:
                options = json.loads(options)
                options_str = json.dumps(options,indent=2)
            else:
                options_str = "None"
            short_type = data[row]['Short Type']
            if short_type == "D":
                obj = pyrplib.dataset.ProcessedD.from_json(link).load()
            description = datasets_df.loc[obj.source_dataset_id,"Description"]
            dataset_name = datasets_df.loc[obj.source_dataset_id,"Dataset Name"]
            command = obj.command

            unprocessed_source_id = obj.source_dataset_id
            unprocessed = pyrplib.dataset.load_unprocessed(unprocessed_source_id,datasets_df)

            index = processed_datasets_df.loc[dataset_id,"Index"]
            description = description.replace("\\n","\n")
            contents = [html.Br(),html.H2(dataset_name),html.H3("Description"),html.Pre(description),html.H3("Command"),html.Pre(command),html.H3("Options"),html.Pre(options_str)]+ [html.H3("Source Item data")] + unprocessed.view_item(index) + [html.H3("Data")] + obj.view()
            return html.Div(contents)
        else:
            return dash.no_update  

def setup_cell_clicked_card(TABLE_ID,OUTPUT_ID,card_class,cards_df):
    @app.callback(
        Output(OUTPUT_ID, "children"),
        Input(TABLE_ID, "active_cell"),
        State(TABLE_ID, "derived_viewport_data"),
    )
    def cell_clicked_card(cell,data):
        if cell is None:
            return dash.no_update
        row,col = cell["row"],cell["column_id"]
        selected = data[row][col]
        if selected is not None:
            dataset_id = data[row]['Dataset ID']
            link = cards_df.set_index('Dataset ID').loc[dataset_id,"Link"]
            options = cards_df.set_index('Dataset ID').loc[dataset_id,"Options"]
            if type(options) == str:
                options = json.loads(options)
                options_str = json.dumps(options,indent=2)
            else:
                options_str = "None"
            obj = card_class.from_json(link)

            processed_datasets_df = config.processed_datasets_df.set_index('Dataset ID') 
            datasets_df = config.datasets_df.set_index('Dataset ID') 
            unprocessed_source_id = processed_datasets_df.loc[obj.source_dataset_id,"Source Dataset ID"]
            description = datasets_df.loc[unprocessed_source_id,"Description"]
            dataset_name = datasets_df.loc[unprocessed_source_id,"Dataset Name"]
            index = processed_datasets_df.loc[obj.source_dataset_id,"Index"]

            unprocessed = pyrplib.dataset.load_unprocessed(unprocessed_source_id,datasets_df)

            contents = [html.Br(),html.H2("Source Dataset Name"),html.P(dataset_name),html.H2("Description"),html.P(description),html.H2("Options"),html.Pre(options_str)] + unprocessed.view_item(index) + obj.view()
            return html.Div(contents)
        else:
            return dash.no_update   
    
########################################################
# Table color/highlight actions
def setup_update_selected_row_color(TABLE_ID):
    @app.callback(
        Output(TABLE_ID, "style_data_conditional"),
        [Input(TABLE_ID, "active_cell")]
    )
    def update_selected_row_color_dataset(active):
        return update_selected_row_color(active)
    
# Define all the callbacks
setup_cell_clicked_dataset()
setup_cell_clicked_processed()
setup_cell_clicked_card(HILLSIDE_TABLE_ID,"hillside_output",pyrplib.card.Hillside,config.hillside_cards_df)
setup_cell_clicked_card(LOP_TABLE_ID,"lop_output",pyrplib.card.LOP,config.lop_cards_df)
setup_cell_clicked_card(MASSEY_TABLE_ID,"massey_output",pyrplib.card.SystemOfEquations,config.massey_cards_df)
setup_cell_clicked_card(COLLEY_TABLE_ID,"colley_output",pyrplib.card.SystemOfEquations,config.colley_cards_df)

setup_update_selected_row_color(UNPROCESSED_TABLE_ID)
setup_update_selected_row_color(PROCESSED_TABLE_ID)
setup_update_selected_row_color(LOP_TABLE_ID)
setup_update_selected_row_color(MASSEY_TABLE_ID)
setup_update_selected_row_color(COLLEY_TABLE_ID)
setup_update_selected_row_color(HILLSIDE_TABLE_ID)