from datetime import timedelta

import pandas as pd

from .. import dataset
from .. import style

selectionSundays = {'2002':'03/10/2002','2003':'03/16/2003',
                    '2004':'03/14/2004','2005':'03/13/2005',
                    '2006':'03/12/2006','2007':'03/11/2007',
                    '2008':'03/16/2008','2009':'03/15/2009',
                    '2010':'03/14/2010','2011':'03/13/2011',
                    '2012':'03/11/2012','2013':'03/17/2013',
                    '2014':'03/16/2014','2015':'03/15/2015',
                    '2016':'03/13/2016','2017':'03/12/2017',
                    '2018':'03/11/2018','2019':'03/17/2019',
                    '2022':'03/13/2022'
                   }   

selectionSundayList = ['03/10/2002','03/16/2003','03/14/2004','03/13/2005','03/12/2006','03/11/2007','03/16/2008',
                       '03/15/2009','03/14/2010','03/13/2011','03/11/2012',
                       '03/17/2013','03/16/2014','03/15/2015','03/13/2016','03/12/2017','03/11/2018', '3/17/2019','03/13/2022']

days_to_subtract=7
d = timedelta(days=days_to_subtract)

# Just a consistent way of processing files. Ignore the fact that the local variables say 2014
def read_data(teams_file,games_file,madness_teams_file):
    teams_2014 = pd.read_csv(teams_file,header=None)
    teams_2014.columns=["number","name"]
    games_2014 = pd.read_csv(games_file,header=None)
    games_2014.columns = ["notsure1","date","team1","H_A_N1","points1","team2","H_A_N2","points2"]
    team1_names = teams_2014.copy()
    team1_names.columns = ["team1","team1_name"]
    team1_names.set_index('team1',inplace=True)
    games_2014 = games_2014.set_index("team1").join(team1_names,how='inner').reset_index()
    team2_names = teams_2014.copy()
    team2_names.columns = ["team2","team2_name"]
    team2_names.set_index('team2',inplace=True)
    games_2014 = games_2014.set_index("team2").join(team2_names,how='inner').reset_index()
    games_2014["date"] = pd.to_datetime(games_2014["date"],format="%Y%m%d")
    games_2014["team1_name"] = games_2014["team1_name"].str.replace(" ","")
    games_2014["team2_name"] = games_2014["team2_name"].str.replace(" ","")
    prev_len = len(games_2014)
    madness_teams = pd.read_csv(madness_teams_file,header=None)
    madness_teams.columns=["name"]
    games_2014["team1_madness"] = 0
    games_2014["team2_madness"] = 0
    mask = games_2014.team1_name.isin(list(madness_teams["name"]))
    games_2014.loc[mask,"team1_madness"] = 1
    mask = games_2014.team2_name.isin(list(madness_teams["name"]))
    games_2014.loc[mask,"team2_madness"] = 1
    games_2014.reset_index()
    for selection_sunday in selectionSundayList:
        games = games_2014.loc[games_2014["date"] <= pd.to_datetime(selection_sunday,format="%m/%d/%Y")-d]
        remaining_games = games_2014.loc[games_2014["date"] > pd.to_datetime(selection_sunday,format="%m/%d/%Y")-d] 
        if len(games) > 0:
            break
    games = games.sort_values(by='date')
    remaining_games.sort_values(by='date')
    return games,remaining_games

class Unprocessed(dataset.Unprocessed):
    def load(self,options={}):
        """Returns a dataframe with outcomes of NCAA March Madness games played.
        """

        teams_file,games_file,madness_teams_file = self.links
        games,remaining_games = read_data(teams_file,games_file,madness_teams_file)

        self.game_df = pd.DataFrame({"team1_name":games['team1_name'],
                    "team1_score":games['points1'],
                    "team1_H_A_N": games['H_A_N1'],
                    "team2_name":games['team2_name'],
                    "team2_score":games['points2'],
                    "team2_H_A_N": games['H_A_N1']})
        
        self.madness_teams = list(pd.read_csv(madness_teams_file,header=None).iloc[:,0])
        
        self._data = pd.DataFrame([[self.game_df,self.madness_teams]],columns=["game_df","madness_teams"])
        
        return self
    
    def type(self):
        return str(dataset.UnprocessedType.Games)
        
    def dash_ready_data(self):
        return self.data()