import pandas as pd

from .. import dataset
from .. import style

class Unprocessed(dataset.Unprocessed):
    def load(self,options={}):
        """Returns a dataframe with outcomes of NCAA March Madness games played.
        :rtype: pd.DataFrame
        :return: dataframe of games with team names, scores, and home/away/neutral location notes
        """
        from marchmadness_study import base

        teams_file,games_file,madness_teams_file = self.links
        games,remaining_games = base.read_data(teams_file,games_file,madness_teams_file)

        self.game_df = pd.DataFrame({"team1_name":games['team1_name'],
                    "team1_score":games['points1'],
                    "team1_H_A_N": games['H_A_N1'],
                    "team2_name":games['team2_name'],
                    "team2_score":games['points2'],
                    "team2_H_A_N": games['H_A_N1']})
        
        self.madness_teams = list(pd.read_csv(madness_teams_file,header=None).iloc[:,0])
        
        return self
    
    def data(self):
        return self.game_df,self.madness_teams
        
    def view(self):
        return style.get_standard_data_table(self.game_df,"game_df")

       
