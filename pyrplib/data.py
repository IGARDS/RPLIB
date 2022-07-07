import pandas as pd
import csv
import os

import importlib

from . import card
from . import dataset as pydataset

class Data:
    """
    A class that facilitates accessing the datasets for RPLIB. 
    
    This class reads the following TSV files:
        * {DATA_PREFIX}/unprocessed_datasets.tsv
            * Columns: Dataset ID, Dataset Name, Description, Type, Loader, Download links
            * Dataset ID - persistant unique ID for each dataset
            * Dataset Name - Short human readable name for the dataset
            * Description - Longer human readable description of the dataset
            * Type - Games|D matrix|Features|Structured Artificial
            * Loader - Class that is used to load the dataset (e.g., marchmadness.base.Unprocessed)
            * Download links - String of comma separated file links
        * {DATA_PREFIX}/processed_datasets.tsv
            * Columns: Dataset ID, Source Dataset ID, Index, Command, Type, Collection, Options, Last Processed Datetime, Identifier
            * Dataset ID - persistant unique ID for each processed dataset
            * Source Dataset ID - source dataset ID
            * Index - Index pointing into the source dataset to extract the specific value
            * Command - Python functional code statement describing how to process the data. May assume the following variables: data and index.
            * Type - resulting type of dataset (D|Games)
            * Collection - Name of collection for organization in the data directory
            * Options - JSON string of optional options
            * Last Processed Datetime - Last time this dataset was processed/updated
            * Identifier - Optional identifying string for the dataset
        * {DATA_PREFIX}/lop_cards.tsv
            * Columns: Dataset ID, Processed Dataset ID, Options, Last Processed Datetime
            * Dataset ID - persistant unique ID for each card
            * Processed Dataset ID - processed dataset ID used as input
            * Options - JSON string of optional options
            * Last Processed Datetime - Last time this dataset was processed/updated
        * {DATA_PREFIX}/hillside_cards.tsv
            * Columns: Dataset ID, Processed Dataset ID, Options, Last Processed Datetime
            * Dataset ID - persistant unique ID for each card
            * Processed Dataset ID - processed dataset ID used as input
            * Options - JSON string of optional options
            * Last Processed Datetime - Last time this dataset was processed/updated
        * {DATA_PREFIX}/massey_cards.tsv
            * Columns: Dataset ID, Processed Dataset ID, Options, Last Processed Datetime
            * Dataset ID - persistant unique ID for each card
            * Processed Dataset ID - processed dataset ID used as input
            * Options - JSON string of optional options
            * Last Processed Datetime - Last time this dataset was processed/updated
        * {DATA_PREFIX}/colley_cards.tsv
            * Columns: Dataset ID, Processed Dataset ID, Options, Last Processed Datetime
            * Dataset ID - persistant unique ID for each card
            * Processed Dataset ID - processed dataset ID used as input
            * Options - JSON string of optional options
            * Last Processed Datetime - Last time this dataset was processed/updated
    """
    def __init__(self,DATA_PREFIX):
        self.DATA_PREFIX=DATA_PREFIX
        
        self.datasets_df = pd.read_csv(f"{DATA_PREFIX}/unprocessed_datasets.tsv",sep='\t')
        self.datasets_df['Download links'] = self.datasets_df['Download links'].str.split(",")
        self.datasets_df = self.datasets_df.infer_objects()
        
        self.processed_datasets_df = pd.read_csv(f"{DATA_PREFIX}/processed_datasets.tsv",sep='\t')
        self.processed_datasets_df['Link'] = DATA_PREFIX+"/"+self.processed_datasets_df['Collection']+"/"+ self.processed_datasets_df['Dataset ID'].astype(str)+".json"
        self.processed_datasets_df = self.processed_datasets_df.infer_objects()

        self.lop_cards_df = pd.read_csv(f"{DATA_PREFIX}/lop_cards.tsv",sep='\t')
        self.lop_cards_df['Link'] = DATA_PREFIX+"/lop/"+self.lop_cards_df['Dataset ID'].astype(str)+".json"
        self.lop_cards_df = self.lop_cards_df.infer_objects()

        self.hillside_cards_df = pd.read_csv(f"{DATA_PREFIX}/hillside_cards.tsv",sep='\t')
        self.hillside_cards_df['Link'] = DATA_PREFIX+"/hillside/"+self.lop_cards_df['Dataset ID'].astype(str)+".json"
        self.hillside_cards_df = self.hillside_cards_df.infer_objects()
        
        self.massey_cards_df = pd.read_csv(f"{DATA_PREFIX}/massey_cards.tsv",sep='\t')
        self.massey_cards_df['Link'] = DATA_PREFIX+"/massey/"+self.lop_cards_df['Dataset ID'].astype(str)+".json"
        self.massey_cards_df = self.massey_cards_df.infer_objects()
        
        self.colley_cards_df = pd.read_csv(f"{DATA_PREFIX}/colley_cards.tsv",sep='\t')
        self.colley_cards_df['Link'] = DATA_PREFIX+"/colley/"+self.lop_cards_df['Dataset ID'].astype(str)+".json"
        self.colley_cards_df = self.colley_cards_df.infer_objects()
        
    def _prepare_for_save(self,sel_datasets_df):
        sel_datasets_df = sel_datasets_df.copy()
        if sel_datasets_df.index.name == "Dataset ID":
            sel_datasets_df.reset_index(inplace=True)
        sel_datasets_df.drop("Link",axis=1,inplace=True)
        return sel_datasets_df
    
    def save_processed_datasets(self):
        df = self._prepare_for_save(self.processed_datasets_df)
        df.to_csv(f"{self.DATA_PREFIX}/processed_datasets.tsv",sep='\t',index=False)
        
    def save_lop_datasets(self):
        df = self._prepare_for_save(self.lop_cards_df)
        df.to_csv(f"{self.DATA_PREFIX}/lop_cards.tsv",sep='\t',index=False)
        
    def save_hillside_datasets(self):
        df = self._prepare_for_save(self.hillside_cards_df)
        df.to_csv(f"{self.DATA_PREFIX}/hillside_cards.tsv",sep='\t',index=False)
        
    def save_massey_datasets(self):
        df = self._prepare_for_save(self.massey_cards_df)
        df.to_csv(f"{self.DATA_PREFIX}/massey_cards.tsv",sep='\t',index=False)

    def save_colley_datasets(self):
        df = self._prepare_for_save(self.colley_cards_df)
        df.to_csv(f"{self.DATA_PREFIX}/colley_cards.tsv",sep='\t',index=False)
        
    def load_unprocessed(self,dataset_id):
        dataset = self.datasets_df.set_index('Dataset ID').loc[dataset_id]
        links = dataset['Download links']
        loader = dataset['Loader']

        loader_lib = ".".join(loader.split(".")[:-1])
        cls_str = loader.split(".")[-1]
        load_lib = importlib.import_module(f"pyrplib.{loader_lib}")
        cls = getattr(load_lib, cls_str)
        unprocessed = cls(dataset_id,links).load()
        
        return unprocessed
    
    def load_processed(self,dataset_id):
        processed_datasets_df = self.processed_datasets_df.set_index('Dataset ID') 
        processed_dataset = processed_datasets_df.loc[dataset_id]
        link = processed_dataset['Link']
        if processed_dataset['Type'] == "D":
            d = pydataset.ProcessedD.from_json(link).load()
        elif processed_dataset['Type'] == "Games":
            d = pydataset.ProcessedGames.from_json(link).load()
        return d
            
    def load_card(self,dataset_id,card_type):
        if card_type == 'lop':
            card_dataset = self.lop_cards_df.set_index('Dataset ID').loc[dataset_id]
            mycard = card.LOP.from_json(card_dataset['Link'])
        elif card_type == 'hillside':
            card_dataset = self.hillside_cards_df.set_index('Dataset ID').loc[dataset_id]
            mycard = card.Hillside.from_json(card_dataset['Link'])
        elif card_type == 'massey':
            card_dataset = self.massey_cards_df.set_index('Dataset ID').loc[dataset_id]
            mycard = card.SystemOfEquations.from_json(card_dataset['Link'])   
        elif card_type == 'colley':
            card_dataset = self.colley_cards_df.set_index('Dataset ID').loc[dataset_id]
            mycard = card.SystemOfEquations.from_json(card_dataset['Link']) 
        return mycard
