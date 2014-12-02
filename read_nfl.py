import csv
import os
from collections import Counter

league = ['SEA', 'GB', 'ATL', 'NO', 'BAL', 'CIN', 'CHI', 'BUF', 'HOU', 
	'WAS', 'KC', 'TEN', 'MIA', 'NE', 'NYJ', 'OAK', 'PHI', 'JAC', 'PIT', 
	'CLE', 'STL', 'MIN', 'DAL', 'SF', 'TB', 'CAR', 'DEN', 'IND', 'DET', 
	'NYG', 'ARI', 'SD']

# returns dictionaries for team offense and team defense, dictionary entries are by
# team_offense[team][season][week] = {total offensive stats}
def read_team_data(seasons=range(2010,2014), weeks=range(1,18), teams=league):
	team_offense = {}
	team_defense = {}
	for team in teams:
		team_offense[team] = {}
		team_defense[team] = {}
		for season in seasons:
			team_offense[team][season] = {}
			team_defense[team][season] = {}
			for week in weeks:
				filename = "../nfl_team_data/" + team + '_' + str(season) + '_' + str(week) + '.csv'
				# no game in this week
				if not os.path.exists(filename):
					team_offense[team][season][week] = None
					team_defense[team][season][week] = None
					continue
				offense_stats = Counter()
				defense_stats = Counter()
				with open(filename) as game:
					gamereader = csv.DictReader(game)
					opponent = None
					for player in gamereader:
						game_stats = Counter(extract_game_stats(player))
						if player['team'] == team: # update offensive stats
							offense_stats = offense_stats + game_stats
						else: # update defensive stats
							opponent = player['team']
							defense_stats = defense_stats + game_stats
				# add entry for the opponent
				offense_stats['opp'] = opponent
				defense_stats['opp'] = opponent
				team_offense[team][season][week] = offense_stats
				team_defense[team][season][week] = defense_stats
	return team_offense, team_defense


# seasons and weeks are lists of seasons and weeks to read data for.
def read_player_data(seasons=range(2010,2014), weeks=range(1,18)):
	# dictionary player_scores[player_id][year][week] = FF score for player in that week of that year (None if they didnt play)
	# dic player_info[player_id] to (name, team, pos)
	player_scores = {}
	player_info = {}
	player_stats = {}
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
						player_stats[player_id][season][week] = game_stats
					else:
						# initialize empty dict for seasons, weeks
						season_dict = {}
						for season_year in seasons:
							week_dict = {}
							for week_number in weeks:
								week_dict[week_number] = None
							season_dict[season_year] = week_dict
						player_scores[player_id] = season_dict
						player_stats[player_id] = season_dict
                        player_info[player_id] = (player['name'], player['team'], player['pos']) 						
	return player_info, player_scores

# some games are missing stats like puntret_tds, this avoids errors associated with missing stat headings
def safe_stat_read(player, stat):
	if stat in player:
		return float(player[stat] or '0')
	else:
		return 0

# given a player dictionary object for a game, returns a new dictionary containing only the necessary stats.
def extract_game_stats(player):
	stats = {}
	stats['home'] = (player['home'] == 'yes')
	stats['passing_att'] = float(player['passing_att'] or '0')
	stats['passing_cmp'] = float(player['passing_cmp'] or '0')
	stats['passing_yds'] = float(player['passing_yds'] or '0')
	stats['passing_tds'] = float(player['passing_tds'] or '0')
	stats['passing_ints'] = float(player['passing_ints'] or '0')
	stats['rushing_att'] = float(player['rushing_att'] or '0')
	stats['rushing_yds'] = float(player['rushing_yds'] or '0')
	stats['rushing_tds'] = float(player['rushing_tds'] or '0')
	stats['receiving_rec'] = float(player['receiving_rec'] or '0')
	stats['receiving_yds'] = float(player['receiving_yds'] or '0')
	stats['receiving_tds'] = float(player['receiving_tds'] or '0')
	stats['ret_tds'] = safe_stat_read(player, 'puntret_tds')
	stats['ret_tds'] += safe_stat_read(player, 'kickret_tds')
	stats['fumbles_lost'] = safe_stat_read(player, 'fumbles_lost')
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