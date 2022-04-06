import importlib
import traceback

import pandas as pd

import pyrankability
import pyrplib

from .common import Method

def get_datasets(config):
    columns = ["Dataset ID","Dataset Name","Type","Length of Data","Description"]
    df = pd.DataFrame(columns=columns).set_index("Dataset ID")

    datasets_df = config.datasets_df.set_index('Dataset ID')
    for index in datasets_df.index:
        new_df = pd.DataFrame(columns=columns).set_index('Dataset ID')
        links = datasets_df.loc[index,'Download links']
        loader = datasets_df.loc[index,'Loader']

        loader_lib = ".".join(loader.split(".")[:-1])
        cls_str = loader.split(".")[-1]
        load_lib = importlib.import_module(f"pyrplib.{loader_lib}")
        cls = getattr(load_lib, cls_str)
        unprocessed = cls(index,links).load()
        
        new_df.loc[index,"Dataset Name"] = datasets_df.loc[index,"Dataset Name"] 
        new_df.loc[index,"Description"] = datasets_df.loc[index,"Description"]
        new_df.loc[index,"Type"] = unprocessed.type()
        new_df.loc[index,"Length of Data"] = len(unprocessed.data())
        df = df.append(new_df)
        
    df = df.sort_values(by='Dataset Name').reset_index()
    
    return df

def get_processed(config):
    datasets_df = df = config.datasets_df.set_index('Dataset ID')
    df = config.processed_datasets_df.copy()
            
    def process(row):
        entry = pd.Series(index=['Dataset ID','Source Dataset ID','Source Dataset Name','Identifier','Short Type','Type','Command','Size','Download'])
        link = row['Link']
        entry['Dataset ID'] = row['Dataset ID']
        try:
            if row['Type'] == "D":
                d = pyrplib.dataset.ProcessedD.from_json(link).load()
            elif row['Type'] == "Games":
                d = pyrplib.dataset.ProcessedGames.from_json(link).load()
            entry.loc['Source Dataset ID'] = d.source_dataset_id
            entry.loc['Source Dataset Name'] = datasets_df.loc[d.source_dataset_id,"Dataset Name"]
            entry.loc['Identifier'] = row['Identifier']
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
