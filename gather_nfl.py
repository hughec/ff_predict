# uses nflgame to gather game data from nfl.com, saves csv files for each week in each season 2010-2013.

import nflgame
import csv


seasons = range(2010,2015)
weeks = range(1,18)
teams = ['SEA', 'GB', 'ATL', 'NO', 'BAL', 'CIN', 'CHI', 'BUF', 'HOU', 
	'WAS', 'KC', 'TEN', 'MIA', 'NE', 'NYJ', 'OAK', 'PHI', 'JAC', 'PIT', 
	'CLE', 'STL', 'MIN', 'DAL', 'SF', 'TB', 'CAR', 'DEN', 'IND', 'DET', 
	'NYG', 'ARI', 'SD']

def gather_players(seasons, weeks):
	for season in seasons:
		for week in weeks:
			game = nflgame.games(season, week=week)
			filename = '../nfl_game_data/' + str(season) + '_' + str(week) + '.csv'
                        try:
                                nflgame.combine_game_stats(game).csv(filename)
                        except TypeError:
                                continue

def gather_teams(seasons, weeks, teams):
	for team in teams:
		for season in seasons:
			for week in weeks:
				filename = '../nfl_team_data/' + team + '_' + str(season) + '_' + str(week) + '.csv'
				# Get game for team in season and week, if team is home, save stats for away players
				try:
					game = nflgame.games(season, week=week, home=team)
					# Game not played yet, break
					if len(game) == 0: break
					game[0].players.csv(filename)
					continue
				except TypeError:
					try:	
						game = nflgame.games(season, week=week, away=team)
						# Game not played yet
						if len(game) == 0: break
						# If team is away, save stats for home players
						game[0].players.csv(filename)
						continue
					except TypeError:
					# Team has bye week, do not write file
						continue

gather_players(seasons, weeks)
gather_teams(seasons, weeks, teams)


