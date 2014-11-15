import csv
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn import cross_validation

# seasons and weeks are lists of seasons and weeks to read data for.
# returns three dictionaries with player data, keys are player ids from nfl.com. 
# each value in player_info is a tuple (name, team, position)
# each value in player_scores is a list of fantasy scores.
# each value in player_stats is a list of dictionary objects, 
# where each object contains passing, rushing, and receiving stats.
def read_player_data(seasons=range(2010,2014), weeks=range(1,18)):
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


def baseline_predictions(p_info, p_scores, p_stats):
	squared_error = []
	for p_id in p_info:
		scores = p_scores[p_id]
		if sum(scores) / float(len(scores)) < 5.0: continue
		for week in range(17, len(scores)):
			y = scores[week]
			y_hat = decaying_weighted_average_predict(scores, week)
			squared_error.append((y - y_hat)**2)
	return sum(squared_error) / len(squared_error)


def extract_baseline_features(p_info, p_scores):
	X = []
	y = []
	for p_id in p_info:
		scores = p_scores[p_id]
		if sum(scores) / float(len(scores)) < 5.0: continue
		for week in range(17, len(scores)):
			# phi(x) = [previous_game_score, 2_games_before, 3_games_before]
			phi = [scores[week - 1], scores[week - 2], scores[week - 3]]
			X.append(phi)
			y.append(scores[week])
	return X, y


def loocv_linear_regression(X, Y):
	mse = 0
	loo = cross_validation.LeaveOneOut(len(X))
	regr = LinearRegression()
	for train, test in loo:
		X_train, X_test = [X[i] for i in train], X[test]
		y_train, y_test = [Y[i] for i in train], Y[test]
		regr.fit(X_train, y_train)
		mse += (regr.predict(X_test) - y_test)**2
	return float(mse) / len(X)



# given a player's fantasy football scores, predicts the player's score in the given week
# based on a decaying weighted average over scores in all previous weeks.
def decaying_weighted_average_predict(scores, week):
	X = scores[:week]
	y = scores[week]
	w = np.arange(1.0 / len(X), 1 + 1.0 / len(X), 1.0 / len(X))
	y_hat = sum([X[i] * w[i] for i in range(len(X))]) / sum(w)
	return y_hat



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


# execute when python read_nfl.py is executed
p_info, p_scores, p_stats = read_player_data()
baseline_mse = baseline_predictions(p_info, p_scores, p_stats)
X, y = extract_baseline_features(p_info, p_scores)
lr_mse = loocv_linear_regression(X, y)
print baseline_mse
print lr_mse
