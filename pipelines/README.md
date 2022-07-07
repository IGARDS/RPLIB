# Pipeline 
The pipeline scripts available in this directory are designed for developers looking to add or update entries into RPLIB. For the general user, these scripts and their associated dependencies are not necessary to interact with RPLIB.

## Setup
LOP and Hillside algorithms rely on both Gurobi and SCIP as solvers. For information on installing Gurobi visit https://support.gurobi.com/hc/en-us/articles/360040541251. For information on installing SCIP visit https://www.scipopt.org/.  

Helper scripts for SCIP must be available on the PATH. Here is an example setup:
```
RANKING_TOOLBOX_DIR=$HOME/ranking_toolbox

SCIP_BIN_DIR=/usr/local/SCIPOptSuite/bin

export PATH=$PATH:$SCIP_BIN_DIR:$RANKING_TOOLBOX_DIR/scip

which scip

which scip_collect.sh

which scip_count.sh

## Examples
### Example running of a Colley card with analsis

```
RPLIB_DATA_PREFIX=$HOME/RPLib/data/ python run.py colley 1
```

### Example process

```
RPLIB_DATA_PREFIX=$HOME/RPLib/data/ python process.py 1
```