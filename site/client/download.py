from io import BytesIO
import io
import diskcache
import zipfile
import tempfile
import os
import urllib
import requests

import dash
from dash.dependencies import Input, Output, State
from dash import dcc

import pyrplib

from . import app
from .identifier import *
from .common import *

config = pyrplib.data.Data(RPLIB_DATA_PREFIX)

def get_all_download_links_from_table(table_data, download_link_attribute):
    def unprocess_link(link, row):
        start = link.rfind('](')
        if start == -1:
            print('Attempted to strip processing on an unprocessed link')
            return -1
        return {'filename' : str(row['Dataset ID'])+'_'+link[1:start], 'link' : link[start+2:-1]}

    unprocessed_links = []
    for dataset in range(len(table_data)):
        for link in table_data[dataset][download_link_attribute].split(', '):
            unprocessed_link = unprocess_link(link, table_data[dataset])
            if unprocessed_link != -1:
                unprocessed_links.append(unprocessed_link)
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

def download_and_or_get_files(data, link_att_name, zipfilename, set_progress=None, total_df=None):
    mf = io.BytesIO()
    if link_att_name:
        download_links = get_all_download_links_from_table(data, link_att_name)
    else:
        # If there is no download link column in the dash table (get download links from the original config table)
        filtered_df = total_df[total_df['Dataset ID'].isin({x['Dataset ID'] for x in data})]
        download_links = [{'filename': x.strip('/app'), 'link': x} for x in filtered_df['Link'].tolist()]
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

def setup_download_button(download_all_button_id, download_all_id, 
                          table_id, link_att_name, suggested_zipfilename, progress_id=None, total_df=None):
    if progress_id:
        # progress bar linking and multiprocessing through long callback
        @app.long_callback(
            output=Output(download_all_id, "data"),
            inputs=(Input(download_all_button_id, "n_clicks"),
                    State(table_id, "derived_virtual_data")),
            progress=[Output(progress_id, "value"),
                    Output(progress_id, "max")]
        )
        def download_all_files(set_progress, n_clicks, data):
            if n_clicks != None:
                path_to_local_zipfile = download_and_or_get_files(data, link_att_name, 
                                                                  suggested_zipfilename, set_progress, total_df)
                return dcc.send_file(path_to_local_zipfile)
    else:
        # no progress bar
        @app.callback(
            Output(download_all_id, "data"),
            Input(download_all_button_id, "n_clicks"),
            State(table_id, "derived_virtual_data")
        )
        def download_all_files(n_clicks, data):
            if n_clicks != None:
                path_to_local_zipfile = download_and_or_get_files(data, link_att_name, 
                                                                  suggested_zipfilename, total_df=total_df)
                return dcc.send_file(path_to_local_zipfile)

def setup_download_progress_bar(download_progress_collapse_id, download_all_button_id, download_progress_id):
    @app.callback(
        Output(download_progress_collapse_id, "is_open"),
        Input(download_all_button_id, "n_clicks"),
        Input(download_progress_id, "value"),
        Input(download_progress_id, "max"),
        State(download_progress_collapse_id, "is_open")
    )
    def progess_bar_display(n_clicks, progress_val, progress_max, is_open):
        if n_clicks:
            # the progress becomes undefined when finished
            if progress_val is None or progress_max is None:
                return False
            return True
        else:
            return is_open

# setup_download_button(PROCESSED_TABLE_DOWNLOAD_ALL_BUTTON_ID, PROCESSED_TABLE_DOWNLOAD_ALL_ID,
#                       PROCESSED_TABLE_ID, "Download", "processed.zip", PROCESSED_TABLE_DOWNLOAD_PROGRESS_ID)
# setup_download_progress_bar(PROCESSED_TABLE_DOWNLOAD_PROGRESS_COLLAPSE_ID, PROCESSED_TABLE_DOWNLOAD_ALL_BUTTON_ID,
#                             PROCESSED_TABLE_DOWNLOAD_PROGRESS_ID)

# Uses the regular callback without the progress bar and without multiprocessing
setup_download_button(PROCESSED_TABLE_DOWNLOAD_ALL_BUTTON_ID, PROCESSED_TABLE_DOWNLOAD_ALL_ID,
                      PROCESSED_TABLE_ID, None, "processed.zip", total_df=config.processed_datasets_df.copy())
setup_download_button(LOP_TABLE_DOWNLOAD_ALL_BUTTON_ID, LOP_TABLE_DOWNLOAD_ALL_ID,
                      LOP_TABLE_ID, None, "lop.zip", total_df=config.lop_cards_df.copy())
setup_download_button(HILLSIDE_TABLE_DOWNLOAD_ALL_BUTTON_ID, HILLSIDE_TABLE_DOWNLOAD_ALL_ID,
                      HILLSIDE_TABLE_ID, None, "hillside.zip", total_df=config.hillside_cards_df.copy())
setup_download_button(MASSEY_TABLE_DOWNLOAD_ALL_BUTTON_ID, MASSEY_TABLE_DOWNLOAD_ALL_ID,
                      MASSEY_TABLE_ID, None, "massey.zip", total_df=config.massey_cards_df.copy())
setup_download_button(COLLEY_TABLE_DOWNLOAD_ALL_BUTTON_ID, COLLEY_TABLE_DOWNLOAD_ALL_ID,
                      COLLEY_TABLE_ID, None, "colley.zip", total_df=config.colley_cards_df.copy())

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