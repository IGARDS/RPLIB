import requests
import json

import pandas as pd

from .. import dataset
from .. import style

class Unprocessed(dataset.Unprocessed):
    def load(self,options={}):
        """
        """
        self._data = None
        for i,link in enumerate(self.links):
            try:
                contents = json.loads(open(link).read())
            except:
                contents = requests.get(link).json()
            contents = pd.Series(contents,name=i)
            if self._data is None:
                self._data = pd.DataFrame(columns=contents.index)
            self._data = self._data.append(contents)
        return self
    
    def data(self):
        return self._data,
        
    def view(self):
        return style.get_standard_data_table(self._data,"data_year")

       
