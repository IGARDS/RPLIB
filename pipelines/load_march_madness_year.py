import sys
from pathlib import Path

import pandas as pd
import numpy as np

home = str(Path.home())

sys.path.insert(0,"%s"%home)

from ranking_toolbox import pyrankability

from marchmadness_study import base

def load_D_from_games(teams_file,games_file,madness_teams_file):
    games,remaining_games = base.read_data(teams_file,games_file,madness_teams_file)
    
    game_df = pd.DataFrame({"team1_name":games['team1_name'],
                        "team1_score":games['points1'],
                        "team1_H_A_N": games['H_A_N1'],
                        "team2_name":games['team2_name'],
                        "team2_score":games['points2'],
                        "team2_H_A_N": games['H_A_N1']})
    
    madness_teams = list(pd.read_csv(madness_teams_file,header=None).iloc[:,0])
    
    return game_df,madness_teams
    
