from sklearn.linear_model import LinearRegression
from sklearn import cross_validation
from collections import Counter

def extract_baseline_features(p_scores):
	X = []
	y = []
	for p_id in p_scores:
		scores = [0]
		p_seasons = p_scores[p_id]
		for season in p_seasons:
			p_weeks = p_seasons[season]
			for week in p_weeks:
				if p_weeks[week] is not None:
					scores.append(p_weeks[week])
		#Filter out players with low scores
                if sum(scores) / float(len(scores)) < 5.0: continue
		for week in range(17, len(scores)):
			# phi(x) = [previous_game_score, 2_games_before, 3_games_before]
			phi = [scores[week - 1], scores[week - 2], scores[week - 3]]
			X.append(phi)
			y.append(scores[week])
	return X, y

def build_phi(p_info, p_scores, p_stats, team_o, team_d, p_id, season, week):
        phi = []
        
        #Previous 5 game scores
        scores = [p_scores[p_id][s][w] for s in p_scores[p_id] for w in p_scores[p_id][s] \
                  if s <= season and (w < week or s < season) and p_scores[p_id][s][w] is not None]
        #Add 0's if not enough games are seen
        scores = [0 for i in range(5-len(scores))] + scores
        phi += scores[-5:]

        # scores for previous 5 home/away games
        #HACK for bug getting home games which is sometimes broke (just assumes that they are at home)
        try:
                game_at_home = p_stats[p_id][season][week]['home']
        except TypeError:
                game_at_home = True

        home_away_scores = [p_scores[p_id][s][w] for s in p_scores[p_id] for w in p_scores[p_id][s] \
                  if s <= season and (w < week or s < season) and p_scores[p_id][s][w] is not None \
                  and p_stats[p_id][s][w]['home'] == game_at_home]
        home_away_scores = [0 for i in range(5-len(home_away_scores))] + home_away_scores
        phi += home_away_scores[-5:]
        # scores for previous 3 games vs. opponent
        player_team = p_info[p_id][1]
        if team_o[player_team][season][week]:
        	opponent = team_o[player_team][season][week]['opp']
        else:
        	#print p_info[p_id], season, week
        	opponent = None
        vs_opp_scores = [p_scores[p_id][s][w] for s in p_scores[p_id] for w in p_scores[p_id][s] \
                  if s <= season and (w < week or s < season) and p_scores[p_id][s][w] is not None \
                  and team_o[player_team][s][w] is not None and team_o[player_team][s][w]['opp'] == opponent]
        vs_opp_scores = [0 for i in range(3-len(vs_opp_scores))] + vs_opp_scores
        phi += vs_opp_scores[-3:]


       	stats_to_include = ['passing_cmp', 'passing_yds', 'passing_tds',
       						'receiving_rec', 'receiving_yds', 'receiving_tds',
       						'rushing_att', 'rushing_yds', 'rushing_tds']
       	d_avg = Counter()
       	for stat in stats_to_include:
       		d_avg[stat] = 0
        # opponent defensive stats over last 5 games
        d_last_5 = []
        if opponent is not None: # this should indicate that this is a bye week
        	d_last_N = [team_d[opponent][s][w] for s in team_d[opponent] for w in team_d[opponent][s]
	        			if s <= season and (w < week or s < season) and team_d[opponent][s][w] is not None]
	        if len(d_last_N) >= 5:
	        	d_last_5 = d_last_N[-5:]
	        else:
	        	d_last_5 = d_last_N

	        for game in d_last_5:
	        	d_avg += game

       	# offensive stats for player's team over last 5 games
        o_last_N = [team_o[player_team][s][w] for s in team_o[player_team] for w in team_o[player_team][s]
        			if s <= season and (w < week or s < season) and team_o[player_team][s][w] is not None]
        if len(o_last_N) >= 5:
        	o_last_5 = o_last_N[-5:]
        else:
        	o_last_5 = o_last_N

        player_last_N = [p_stats[p_id][s][w] for s in p_stats[p_id] for w in p_stats[p_id][s]
        			if s <= season and (w < week or s < season) and p_stats[p_id][s][w] is not None]
        if len(player_last_N) >= 5:
        	player_last_5 = player_last_N[-5:]
        else:
        	player_last_5 = player_last_N

        # player's average share of team's offensive stats over last 5 games
        player_shares_avg = Counter()
        for i in range(len(player_last_5)):
        	for stat in stats_to_include:
        		if o_last_5[i][stat] == 0:
        			player_shares_avg[stat] = 0
        		else:
        			player_shares_avg[stat] = player_last_5[i][stat] / o_last_5[i][stat]

       	for stat in stats_to_include:
       		# compute averages
       		player_shares_avg[stat] = player_shares_avg[stat] / len(o_last_5)
       		if len(d_last_5) > 0:
       			d_avg[stat] = d_avg[stat] / len(d_last_5)
       		# add features to feature vector phi
	       	phi += [d_avg[stat]]
       		phi += [player_shares_avg[stat]]
       		phi += [player_shares_avg[stat] * d_avg[stat]]

       	#Other features...


        return phi

def extract_features(p_info, p_scores, p_stats, team_o, team_d):
        X = []
        y = []
        for p_id in p_scores:
                for season in p_scores[p_id]:
                        for week in p_scores[p_id][season]:
                                if p_scores[p_id][season][week] is not None:
                                        X.append(build_phi(p_info, p_scores,  p_stats, team_o, team_d, p_id, season, week))
                                        y.append(p_scores[p_id][season][week])
        return X,y

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

def train_regression(X,Y):
        regr = LinearRegression()
        regr.fit(X, Y)
        return regr
