import pandas as pd

from .. import dataset
from .. import style

class Unprocessed(dataset.Unprocessed):
    def load(self,options={}):
        """Returns a D matrix dataframe from the LOLib
        :rtype: pd.DataFrame
        :return: dataframe of IO lib data
        """
        from lolib_study import base
        D = base.read_instance_url(*self.links)
        self.D = D      
        return self
    
    def data(self):
        return self.D,
    
    def view(self):
        return style.get_standard_data_table(self.D,"lolib_data")

       
