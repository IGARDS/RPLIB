import pandas as pd
import csv

class Config:
    def __init__(self,DATA_PREFIX):
        self.DATA_PREFIX=DATA_PREFIX
        self.datasets_df = pd.read_csv(f"{DATA_PREFIX}/unprocessed_datasets.tsv",sep='\t')
        self.datasets_df['Download links'] = self.datasets_df['Download links'].str.split(",")
        self.datasets_df = self.datasets_df.infer_objects()
        
        self.processed_datasets_df = pd.read_csv(f"{DATA_PREFIX}/processed_datasets.tsv",sep='\t')
        self.processed_datasets_df['Link'] = DATA_PREFIX+"/"+self.processed_datasets_df['Collection']+"/"+ self.processed_datasets_df['Dataset ID'].astype(str)+".json"

        self.lop_cards_df = pd.read_csv(f"{DATA_PREFIX}/lop_cards.tsv",sep='\t')
        self.lop_cards_df['Link'] = DATA_PREFIX+"/"+self.lop_cards_df['Collection']+"/"+self.lop_cards_df['Dataset ID'].astype(str)+".json"
        
        self.hillside_cards_df = pd.read_csv(f"{DATA_PREFIX}/hillside_cards.tsv",sep='\t')
        self.hillside_cards_df['Link'] = DATA_PREFIX+"/"+self.hillside_cards_df['Collection']+"/"+self.hillside_cards_df['Dataset ID'].astype(str)+".json"
        
        self.massey_cards_df = pd.read_csv(f"{DATA_PREFIX}/massey_cards.tsv",sep='\t')
        self.massey_cards_df['Link'] = DATA_PREFIX+"/"+self.massey_cards_df['Collection']+"/"+self.massey_cards_df['Dataset ID'].astype(str)+".json"
        
        self.colley_cards_df = pd.read_csv(f"{DATA_PREFIX}/colley_cards.tsv",sep='\t')
        self.colley_cards_df['Link'] = DATA_PREFIX+"/"+self.colley_cards_df['Collection']+"/"+self.colley_cards_df['Dataset ID'].astype(str)+".json"
        
    def save_processed_datasets(self):
        self.processed_datasets_df.drop("Link",axis=1,inplace=True)
        self.processed_datasets_df.to_csv(f"{self.DATA_PREFIX}/processed_datasets.tsv",sep='\t')
