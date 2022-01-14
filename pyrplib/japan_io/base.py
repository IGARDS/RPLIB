import pandas as pd

from .. import dataset
from .. import style

class Unprocessed(dataset.Unprocessed):
    def load(self,options={}):
        """Returns a D matrix dataframe from the Japan csv files
        :rtype: pd.DataFrame
        :return: dataframe of IO Japan data
        """
        D = pd.read_csv(*self.links,header=None)
        self.D = D      
        return self
    
    def data(self):
        return self.D,
    
    def view(self):
        return style.get_standard_data_table(self.D,"japan_io_data")

       
