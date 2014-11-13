import csv

# seasons and weeks are lists of seasons and weeks to read data for.
# returns three dictionaries with player data, keys are player ids from nfl.com. 
# each value in player_info is a tuple (name, team, position)
# each value in player_scores is a list of fantasy scores.
# each value in player_stats is a list of dictionary objects, 
# where each object contains passing, rushing, and receiving stats.
def read_player_data(seasons=range(2010,2014), weeks=range(1,17)):
	player_info = {}
	player_scores = {}
	player_stats = {}
	for season in seasons:
		for week in weeks:
			filename = '../nfl_game_data/' + str(season) + '_' + str(week) + '.csv'
			with open(filename) as games:
				gamesreader = csv.DictReader(games)
				for player in gamesreader:
					# only include skill positions
					if player['pos'] not in ['QB', 'RB', 'FB', 'WR', 'TE', '']: continue
					p_id = player['id']
					game_stats = extract_game_stats(player)
					if p_id in player_info:
						player_scores[p_id].append(yahoo_fantasy_score(game_stats))
						player_stats[p_id].append(game_stats)
					else:
						player_info[p_id] = (player['name'], player['team'], player['pos'])
						player_scores[p_id] = [yahoo_fantasy_score(game_stats)]
						player_stats[p_id] = [game_stats]
	return player_info, player_scores, player_stats


def decaying_weighted_average_predict(scores, week):
	X = scores[:week]
	y = scores[week]
	w = xrange(0, 1, 10.0 / len(X))
	y_hat = sum([X[i] * w[i] for i in range(len(X))])
	return y, y_hat



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
