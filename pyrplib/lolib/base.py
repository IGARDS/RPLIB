import pandas as pd

from io import StringIO
import urllib

import pandas as pd

import urllib.request

def read_instance(content):
    lines = content.strip().split("\n")[1:]
    data_str = ("\n".join([line.strip() for line in lines])).replace(" ",",")
    df = pd.read_csv(StringIO(data_str),header=None)
    return df

def read_instance_url(link):
    resource = urllib.request.urlopen(link)
    return read_instance(resource.read().decode(resource.headers.get_content_charset()))

from .. import dataset
from .. import style

class Unprocessed(dataset.Unprocessed):
    def load(self,options={}):
        """Returns a D matrix dataframe from the LOLib
        :rtype: pd.DataFrame
        :return: dataframe of IO lib data
        """
        D = read_instance_url(*self.links)
        self.D = D 
        
        self._data = pd.DataFrame([[self.D]],columns=["D"])
        
        return self
    
    def type(self):
        return str(dataset.UnprocessedType.D)
    
    def dash_ready_data(self):
        return self.data()

       
