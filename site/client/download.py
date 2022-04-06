from io import BytesIO
import io
import diskcache
import zipfile
import tempfile
import os
import urllib

import dash
from dash.dependencies import Input, Output, State
from dash import dcc

from . import app
from .identifier import *

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