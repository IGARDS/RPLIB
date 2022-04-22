# Pipeline 
## Setup
Example setup below. Your system may vary.
```
RANKING_TOOLBOX_DIR=$HOME/ranking_toolbox

SCIP_BIN_DIR=/usr/local/SCIPOptSuite/bin

export PATH=$PATH:$SCIP_BIN_DIR:$RANKING_TOOLBOX_DIR/scip

which scip

which scip_collect.sh

which scip_count.sh

## Example run

```
RPLIB_DATA_PREFIX=$HOME/RPLib/data/ python run.py colley 1
```