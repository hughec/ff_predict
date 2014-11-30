import csv
import os

# seasons and weeks are lists of seasons and weeks to read data for.
def read_player_data(seasons=range(2010,2014), weeks=range(1,18)):
	# dictionary player_scores[player_id][year][week] = FF score for player in that week of that year (None if they didnt play)
        # dic player_info[player_id] to (name, team, pos)
	player_scores = {}
        player_info = {}
	for season in seasons:
		for week in weeks:
			filename = '../nfl_game_data/' + str(season) + '_' + str(week) + '.csv'
                        if not os.path.exists(filename):
                                continue
			with open(filename) as games:
				gamesreader = csv.DictReader(games)
				for player in gamesreader:
					# only include skill positions
					if player['pos'] not in ['QB', 'RB', 'FB', 'WR', 'TE']: continue
					player_id = player['id']
					game_stats = extract_game_stats(player)
					fantasy_score = yahoo_fantasy_score(game_stats)
					if player_id in player_scores:
						player_scores[player_id][season][week] = fantasy_score
					else:
						season_dict = {}
						for season_year in seasons:
							week_dict = {}
							for week_number in weeks:
								week_dict[week_number] = None
							season_dict[season_year] = week_dict
						player_scores[player_id] = season_dict
                                                player_info[player_id] = (player['name'], player['team'], player['pos']) 						
	return player_info, player_scores

# given a player dictionary object for a game, returns a new dictionary containing only the necessary stats.
def extract_game_stats(player):
	stats = {}
	stats['passing_yds'] = float(player['passing_yds'] or '0')
	stats['passing_tds'] = float(player['passing_tds'] or '0')
	stats['passing_ints'] = float(player['passing_ints'] or '0')
	stats['rushing_yds'] = float(player['rushing_yds'] or '0')
	stats['rushing_tds'] = float(player['rushing_tds'] or '0')
	stats['receiving_yds'] = float(player['receiving_yds'] or '0')
	stats['receiving_tds'] = float(player['receiving_tds'] or '0')
	stats['ret_tds'] = float(player['puntret_tds'] or '0') + float(player['kickret_tds'] or '0')
	stats['fumbles_lost'] = float(player['fumbles_lost'] or '0')
	stats['twoptm'] = float(player['passing_twoptm'] or '0') + float(player['rushing_twoptm'] or '0') + float(player['receiving_twoptm'] or '0')
	return stats


# player_stats is a dictionary containing the game stats of a player in a given week.
# uses yahoo fantasy football scoring to return the score for the given player in the given week.
def yahoo_fantasy_score(player_stats):
	score = 0
	# passing stats
	score += 0.04 * player_stats['passing_yds']
	score += 4 * player_stats['passing_tds']
	score -= 1 * player_stats['passing_ints']
	# rushing stats
	score += 0.1 * player_stats['rushing_yds']
	score += 6 * player_stats['rushing_tds']
	# receiving stats
	score += 0.1 * player_stats['receiving_yds']
	score += 6 * player_stats['receiving_tds']
	# return tds
	score += 6 * player_stats['ret_tds']
	# fumbles
	score -= 2 * player_stats['fumbles_lost']
	# two point conversions
	score += 2 * player_stats['twoptm']
	return score
