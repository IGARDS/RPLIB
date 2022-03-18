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
            Ds_df = pd.DataFrame([Ds]).T
            Ds_df.index.name = "Inner Index"
            Ds_df.columns = ["D"]
            Ds_df = Ds_df.reset_index()
            Ds_df.index = [contents.name]*len(Ds_df)
            contents = contents.to_frame().drop("Ds").T
            contents = contents.join(Ds_df)
            if self._data is None:
                self._data = contents
            else:
                self._data = self._data.append(contents)
        self._data.index.name = "Outer Index"
        self._data.reset_index(inplace=True)
        return self
    
    def dash_ready_data(self):
        return self.data().drop("D",axis=1)
    
    def type(self):
        return str(dataset.UnprocessedType.D)
       
