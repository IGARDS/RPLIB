import pandas as pd
import os

# Constants
UNPROCESSED_FILE_NAME = 'unprocessed_datasets.tsv'
SUCCESS = 'SUCCESS!'
# Main loop
def main(data_path, unprocessed):
    prompt = "Would you like to\n1. A[dd] dataset(s)?\n2. R[emove] dataset(s)?\n" + \
             "3. M[odify] a dataset table?\n4. Q[uit]?\nInput: "
    req = input(prompt).lower().strip()
    while req != '' and req[0] != 'q':
        if req[0] == 'a':
            req = add(data_path, unprocessed)
        elif req[0] == 'r':
            req = remove(data_path)
        elif req[0] == 'm':
            req = modify(data_path)
        elif req == SUCCESS:
            req = input(prompt).lower()
        else:
            print('Unknown option entered')
            req = input(prompt).lower()

def add(data_path, unprocessed):
    # base_loader = get_base_loader()
    print('\nAdd a dataset:\n')
    prompt = "Enter '1' to add a single dataset or anything else\n" + \
             "to add many datasets\nInput: "
    add_type = input(prompt).strip()
    if add_type == 'q':
        return 'q'
    elif add_type == '1':
        return add_single_dataset(data_path, unprocessed)
    else:
        return add_multiple_datasets(data_path, unprocessed)

def add_single_dataset(data_path, unprocessed):
    # Next available Dataset ID
    att = {'Dataset ID' : [str(unprocessed['Dataset ID'].max() + 1)]}
    mask = unprocessed.columns != 'Dataset ID'
    for var in list(unprocessed.columns[mask]):
        inp = input(f"Please provide a '{var}': ")
        if inp == 'q':
            return 'q'
        att[var] = [inp.strip()]
    # Append the one row
    row = pd.DataFrame(att).reindex(columns=unprocessed.columns)
    row.to_csv(data_path + '/unprocessed_datasets.tsv', index=False, header=False, sep='\t', mode='a')
    print(f'\nThe following has been appended to the unprocessed table:\n {row.head()}\n')
    return SUCCESS

def add_multiple_datasets(data_path, unprocessed):
    download_links = get_download_links()
    if download_links == 'q':
        return 'q'
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
            return 'q'
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
    new_rows.to_csv(data_path + '/unprocessed_datasets.tsv', index=False, header=False, sep='\t', mode='a')
    print('\nThe rows have been appended to the unprocessed table.\n' +
          f'Here is a sample of the first 1/2 rows:\n {new_rows.head(n=2)}\n')
    return SUCCESS

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
    prompt = "Please provide the path to the data (i.e. '/RPLib/data'): "
    data_path = input(prompt)
    while not os.path.exists(data_path):
        data_path = input("The provided path doesn't exist, please try again: ").rstrip('/')
    unprocessed = pd.read_csv(data_path + "/" + UNPROCESSED_FILE_NAME, sep='\t')
    print('\nAt any prompt, enter q to exit.\n')
    main(data_path, unprocessed)