# uses nflgame to gather game data from nfl.com, saves csv files for each week in each season 2010-2013.

import nflgame

seasons = [2014]
weeks = range(1,11)

for season in seasons:
	for week in weeks:
		game = nflgame.games(season, week=week)
		filename = '../nfl_game_data/' + str(season) + '_' + str(week) + '.csv'
		nflgame.combine_game_stats(game).csv(filename)