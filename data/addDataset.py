import pandas as pd
import os
import sys
from pathlib import Path
import subprocess

# Constants
SUCCESS = 'SUCCESS!'
HOME = str(Path.home())
RPLIB_DATA_PREFIX = os.environ.get("RPLIB_DATA_PREFIX")
RPLIB_PIPELINES_PREFIX = os.environ.get("RPLIB_PIPELINES_PREFIX")
TRANSFORM_TYPES = ["transformers.count", "transformers.direct", "transformers.indirect", 
                   "transformers.process_D", "transformers.features_to_D", "transformers.standardize_games_teams"]
if RPLIB_DATA_PREFIX is None: # Set default
    RPLIB_DATA_PREFIX=f'{HOME}/RPLib/data'
if RPLIB_PIPELINES_PREFIX is None: # Set default
    RPLIB_PIPELINES_PREFIX=f'{HOME}/RPLib/pipelines'

try:
    import pyrplib as pyrplib
except:
    print('Looking for packages in home directory')
    sys.path.insert(0,f"{HOME}") # Add the home directory relevant paths to the PYTHONPATH
    sys.path.insert(0,f"{HOME}/ranking_toolbox") # Add the home directory relevant paths to the PYTHONPATH
    sys.path.insert(0,f"{HOME}/RPLib") # Add the home directory relevant paths to the PYTHONPATH
    import pyrplib

# Main loop
def main(config):
    prompt = "Would you like to\n1. A[dd] dataset(s)?\n2. R[emove] dataset(s)?\n" + \
             "3. M[odify] a dataset table?\n4. Q[uit]?\nInput: "
    req = input(prompt).lower().strip()
    while req != '' and req[0] != 'q':
        if req[0] == 'a':
            req = add(config)
        elif req[0] == 'r':
            req = remove()
        elif req[0] == 'm':
            req = modify()
        elif req == SUCCESS:
            req = input(prompt).lower()
        else:
            print('Unknown option entered')
            req = input(prompt).lower()

def add(config):
    unprocessed = config.datasets_df
    # base_loader = get_base_loader()
    print('\nAdd a dataset:\n')
    prompt = "Input 'P[rocessed]' for an existing unprocessed dataset being added to the\n" + \
             "processed table or anything else for an entirely new dataset.\nInput: "
    add_type = input(prompt).strip().lower()
    if add_type == 'q':
        return 'q'
    elif 'p' in add_type:
        # this is unimplemented
        return add_processed(config)
    else:
        prompt = "\nEnter '1' to add a single dataset or anything else\n" + \
                 "to add many datasets\nInput: "
        new_add_type = input(prompt).strip()
        if new_add_type == 'q':
            return 'q'
        elif new_add_type == '1':
            unprocessed_add_ret, new_rows = add_single_dataset(unprocessed)
        else:
            unprocessed_add_ret, new_rows = add_multiple_datasets(unprocessed)
        if unprocessed_add_ret == 'q':
            return unprocessed_add_ret
        # Ask if the user wants to also add to the processed table
        prompt = "Would you like to process the dataset(s) and add to the processed table as well?\n" + \
                 "Input 'Y[es]' to request this or anything else to skip.\nInput: "
        processed_add_req = input(prompt).strip().lower()
        if 'y' in processed_add_req:
            return add_processed(config, just_added=new_rows)
        return unprocessed_add_ret

def add_processed(config, just_added=None):
    # add these all to the processed table. then call process.py for the newly added files
    # then can ask if user wants to run an algorithm on the dataset(s) and use 'run.py' to do this
    unprocessed = config.datasets_df
    processed = config.processed_datasets_df
    if just_added is not None:
        # User could want different processing for each dataset or same processing for all datasets
        if len(just_added) > 1:
            prompt = "\nWould you like to process each dataset seperately or alternatively\n" + \
                     "all in the same format? Input 'Y[es]' to process each with a different\n" + \
                     "format or anything else to use the same scheme\nInput: "
            individual_process_req = input(prompt).strip().lower()
            if individual_process_req == 'q':
                return 'q'
            if 'y' in individual_process_req:
                new_rows = []
                new_id = processed['Dataset ID'].max() + 1
                for row in just_added.index:
                    ret, new_row = individually_add_to_process_table(processed, unprocessed_row=just_added.loc[row], new_id=new_id)
                    new_id += 1
                    if ret == 'q':
                        return 'q'
                    new_rows.append(new_row)
            else:
                ret, new_rows = add_all_to_process_table(processed, unprocessed_df=just_added)
        else:
            ret, new_rows = individually_add_to_process_table(processed, unprocessed_row=just_added)
        if ret == 'q':
            return 'q'
        # Run the process pipeline 
        # TODO: This is broken right now
        # path_to_pipelines = RPLIB_PIPELINES_PREFIX
        # while not os.path.exists(path_to_pipelines):
        #     path_to_pipelines = input("Pipelines folder couldn't be found. Enter the path to the RPLib/pipelines folder: ")
        # if len(new_rows) > 1:
        #     subprocess.run([path_to_pipelines + "/process.py", f"{processed['Dataset ID'].max() + 1}:"+ \
        #                                                        f"{processed['Dataset ID'].max() + 1 + len(new_rows)}"])
        # else:
        #     subprocess.run([path_to_pipelines + "/process.py", f"{processed['Dataset ID'].max() + 1}"])
        return SUCCESS
    else:
        # Request info from the user ab the unprocessed table
        print("UNIMPLEMENTED")
        return SUCCESS

def add_all_to_process_table(processed, unprocessed_df):
    att, mask = get_base_att_mask_for_processed(processed, unprocessed_df)
    new_len = len(unprocessed_df['Dataset ID']) - 1
    for var in list(unprocessed_df.columns[mask]):
        inp = input(f"Please provide a '{var}': ")
        if inp == 'q':
            return 'q', None
        att[var] = [inp.strip() for _ in range(new_len)]
    new_rows = pd.DataFrame(att).reindex(columns=processed.columns)
    new_rows.to_csv(RPLIB_DATA_PREFIX + '/processed_datasets.tsv', index=False, header=False, sep='\t', mode='a')
    print(f'\nThe following 1/2 rows have been appended to the processed table:\n {new_rows.head(n=2)}\n')
    return SUCCESS, new_rows

def individually_add_to_process_table(processed, unprocessed_row, new_id=None):
    att, mask = get_base_att_mask_for_processed(processed, unprocessed_row, new_id)
    for var in list(processed.columns[mask]):
        inp = input(f"Please enter a '{var}': ")
        if inp == 'q':
            return 'q', None
        att[var] = [inp.strip()]
    new_row = pd.DataFrame(att).reindex(columns=processed.columns)
    new_row.to_csv(RPLIB_DATA_PREFIX + '/processed_datasets.tsv', index=False, header=False, sep='\t', mode='a')
    print(f'\nThe following has been appended to the processed table:\n {new_row.head()}\n')
    return SUCCESS, new_row

def get_base_att_mask_for_processed(processed, unprocessed, start_dataset_id=None):
    # get_command_type and check one of transform options
    prompt = "\nPlease enter a 'Command'. Your options are combinations of:\n" + "\n".join(TRANSFORM_TYPES) + "\nInput: "
    command = input(prompt)
    # Next available Dataset ID
    new_len = max(len(unprocessed['Dataset ID']) - 1, 1)
    if start_dataset_id is None:
        start_dataset_id = processed['Dataset ID'].max() + 1
    # Don't set these as they are already set, (Link column is added in config and shouldn't be output at all)
    mask = (processed.columns != 'Dataset ID') & (processed.columns != 'Source Dataset ID') & \
           (processed.columns != 'Last Processed Datetime') & (processed.columns != 'Command') & \
           (processed.columns != 'Link')
    att = {'Dataset ID': [d_id for d_id in range(start_dataset_id, start_dataset_id + new_len)],
           'Source Dataset ID': list(unprocessed['Dataset ID']),
           'Last Processed Datetime': [None for _ in range(new_len)], 
           'Command': [command for _ in range(new_len)]}
    return att, mask

def add_single_dataset(unprocessed):
    # Next available Dataset ID
    att = {'Dataset ID' : [str(unprocessed['Dataset ID'].max() + 1)]}
    mask = unprocessed.columns != 'Dataset ID'
    for var in list(unprocessed.columns[mask]):
        inp = input(f"Please provide a '{var}': ")
        if inp == 'q':
            return 'q', None
        att[var] = [inp.strip()]
    # Append the one row
    new_row = pd.DataFrame(att).reindex(columns=unprocessed.columns)
    new_row.to_csv(RPLIB_DATA_PREFIX + '/unprocessed_datasets.tsv', index=False, header=False, sep='\t', mode='a')
    print(f'\nThe following has been appended to the unprocessed table:\n {new_row.head()}\n')
    return SUCCESS, new_row

def add_multiple_datasets(unprocessed):
    download_links = get_download_links()
    if download_links == 'q':
        return 'q', None
    prompt = "\nWould you like to prepend or postpend an incremented integer for the name and\n" + \
             "description of each dataset? You may enter 'pre' or 'post' followed by a number\n" + \
             "or anything else to use the same scheme for all datasets (i.e. 'pre 0')\nInput: "
    pend = input(prompt)
    pre = None
    post = None
    if 'pre' in pend:
        pre = int(pend.rstrip().split()[-1])
    elif 'post' in pend:
        post = int(pend.rstrip().split()[-1])

    # Collect the base values to use in appending the new datasets
    att_base = {}
    mask = (unprocessed.columns != 'Download links') & (unprocessed.columns != 'Dataset ID')
    for var in list(unprocessed.columns[mask]):
        inp = input(f"Please provide a base '{var}': ")
        if inp == 'q':
            return 'q', None
        att_base[var] = inp.strip()
    
    # Next available Dataset ID
    start_id = unprocessed['Dataset ID'].max()
    add_length = len(download_links)

    # Create a dictionary to output the new tsvs
    # Extrapolate the rest of the provided base attributes to the full length of the added datasets
    non_special_mask = (unprocessed.columns != 'Download links') & (unprocessed.columns != 'Dataset ID') & \
                        (unprocessed.columns != 'Dataset Name') & (unprocessed.columns != 'Description')
    att = {col : [att_base[col] for _ in range(add_length)] for col in unprocessed.columns[non_special_mask]}

    att['Dataset ID'] = [str(start_id + i) for i in range(1, add_length + 1)]
    att['Download links'] = download_links
    # pre or postpend the provided numbers if asked to for the Name and Description
    if pre is not None:
        att['Dataset Name'] = [str(prepend) + " " + att_base['Dataset Name'] for prepend in range(pre, pre + add_length)]
        att['Description'] = [str(prepend) + " " + att_base['Description'] for prepend in range(pre, pre + add_length)]
    elif post is not None:
        att['Dataset Name'] = [att_base['Dataset Name'] + " " + str(postpend) for postpend in range(post, post + add_length)]
        att['Description'] = [att_base['Description'] + " " + str(postpend) for postpend in range(post, post + add_length)]
    else:
        att['Dataset Name'] = [att_base['Dataset Name'] for _ in range(add_length)]
        att['Description'] = [att_base['Description'] for _ in range(add_length)]

    # Append the unprocessed table with the new data
    new_rows = pd.DataFrame(att).reindex(columns=unprocessed.columns)
    new_rows.to_csv(RPLIB_DATA_PREFIX + '/unprocessed_datasets.tsv', index=False, header=False, sep='\t', mode='a')
    print('\nThe rows have been appended to the unprocessed table.\n' +
          f'Here is a sample of the first 1/2 rows:\n {new_rows.head(n=2)}\n')
    return SUCCESS, new_rows

# Get the user entered download links
def get_download_links():
    download_links = []
    prompt = "\nEnter a path to a directory of dataset files or a file with a space seperated\n" + \
             "list of links. If entering a directory please ensure it is located\n" + \
             "within the RPLib/data directory.\nInput: "
    # Check directory or file and get all the links here
    file_list = input(prompt).strip()
    good_file = False
    while not good_file:
        if file_list == 'q':
            return 'q'
        if os.path.exists(file_list):
            # this may break the unprocessed table (not sure how the dash app handles the paths here)
            if os.path.isdir(file_list):
                download_links = os.listdir(file_list)
            else:
                link_file = open(file_list, "r")
                download_links = link_file.read().split()
            if download_links != []:
                good_file = True
            else:
                print('The provided directory or file was empty. Please try again.')
                file_list = input('Input: ').strip()
        else:
            print('A bad path was given, please try again.')
            file_list = input('Input: ').strip()
    return download_links

# def get_base_loader():
#     # base_loader_need_prompt = "Does a base loading class already exist? (i.e. pyrplib/marchmadness/base.py): "
#     # base_loader_need = input(base_loader_need_prompt).lower()
#     # while base_loader_need[0] != 'y' and base_loader_need[0] != 'n':
#     #     if base_loader_need[0] == 'q':
#     #         return base_loader_need
#     #     print("Unknown response entered. Please specify 'y', 'n', or 'q'.")
#     #     base_loader_need = input(base_loader_need_prompt).lower()
#     # if base_loader_need == 'y':
#     #     prompt = "Please provide the path to the base loader: "
#     #     data_path = input(prompt)
#     #     while not os.path_exists(data_path):
#     #         data_path = input("The provided path doesn't exist, please try again: ")
#     #     base_loader = 
#     # else:
#     #     base_loader = input("What is the base loader executable? (i.e. 'marchmadness.base.Unprocessed'): ")

def remove():
    pass

def modify():
    pass

if __name__ == "__main__":
    config = pyrplib.config.Config(RPLIB_DATA_PREFIX)
    print("\nAt any prompt, enter 'q' to exit.\n")
    main(config)