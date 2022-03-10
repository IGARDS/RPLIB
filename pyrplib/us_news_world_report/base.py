import pandas as pd

from .. import dataset
from .. import style

class Unprocessed(dataset.Unprocessed):
    def load(self,options={}):
        """Returns a dataframe with features from a year of US News and World Report.
        :rtype: pd.DataFrame
        :return: dataframe of features
        """
        data_year = pd.read_table(*self.links,sep='\t')
        data_year['School Name'] = data_year['School Name'].str.replace('!','')
        if 'State' in data_year.columns:
            data_year['State'] = data_year['State'].str.replace('\(','',regex=True).str.replace('\)','',regex=True)
        df = pd.DataFrame(list(data_year['SAT/ACT 25th-75th Percentile'].str.split('-')),columns=['SAT/ACT 25th Percentile','SAT/ACT 75th Percentile'])
        data_year = pd.concat([data_year,df],axis=1)
        data_year = data_year.infer_objects()
        data_year['SAT/ACT 25th-75th Percentile Mean'] = (data_year['SAT/ACT 25th Percentile'].astype(int)+data_year['SAT/ACT 75th Percentile'].astype(int))/2
        
        self.data_year = data_year#.set_index('School Name')
        return self
    
    def data(self):
        return self.data_year,
        
    def view(self):
        return style.get_standard_data_table(self.data_year,"data_year")

       
