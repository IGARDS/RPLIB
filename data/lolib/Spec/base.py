# Base Functionality for Reading and Processing
import os
from io import StringIO

import pandas as pd

data_dir = os.path.dirname(os.path.abspath(__file__))

def read_instance(name):
    lines = open(f"{data_dir}/{name}").read().strip().split("\n")[1:]
    data_str = ("\n".join([line.strip() for line in lines])).replace(" ",",")
    df = pd.read_csv(StringIO(data_str),header=None)
    return df
