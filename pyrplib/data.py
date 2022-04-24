import pandas as pd
import csv
import os

import importlib

class Data:
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
        df = _prepare_for_save(self.processed_datasets_df)
        df.to_csv(f"{self.DATA_PREFIX}/processed_datasets.tsv",sep='\t',index=False)
        
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
