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
        
        self._data = pd.DataFrame([[self.D]],columns=["D"])
        
        return self
    
    def type(self):
        return str(dataset.UnprocessedType.D)
    
    def dash_ready_data(self):
        return self.data()