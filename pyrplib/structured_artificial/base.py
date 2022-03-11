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
            Ds = {}
            for key in contents["Ds"].keys():
                Ds[key] = pd.DataFrame(contents["Ds"][key])
            contents["Ds"] = pd.Series(Ds)
            if self._data is None:
                self._data = pd.DataFrame(columns=contents.index)
            self._data = self._data.append(contents)
        return self
    
    def data(self): # must return a tuple but there are no other rules!
        return self._data,
        
    def view(self):
        data = self._data.copy()
        data['Shape of Ds'] = data['Ds'].apply(lambda D: ",".join([str(i) for i in D.shape]))
        data.drop('Ds',axis=1,inplace=True)
        return style.get_standard_data_table(data,"data_year")

       
