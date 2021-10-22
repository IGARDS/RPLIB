# RPLib

## Installation instructions

### Step 0. Pre-installation notes
If you wish to run many of the algorithms yourself, you will need to make sure Gurobi and gurobipy is installed within your environment. Gurobi is available to academics free of charge, and you can find those instructions here: https://www.gurobi.com/downloads/end-user-license-agreement-academic/. 

Finally, a lot of the code is built around assuming all paths are relative to your home directory.

### Step 1. Download code and data
git clone https://github.com/IGARDS/RPLib.git

git clone https://github.com/IGARDS/ranking_toolbox

### Step 2. Install dependencies

cd RPLib
pip install -r requirements.txt

## Usage instructions

### Running frontend
The frontend can be run from RPLib/dash directory.

cd RPLib/dash
./run.sh <PORT>
  
Navigate to http://localhost:PORT/
  
### Procesing a file example
  
python $HOME/RPLib/pipelines/create_lop_card.py 13 13
