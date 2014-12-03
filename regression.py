from sklearn.linear_model import LinearRegression
from sklearn import cross_validation

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
        
        #Other features...

        # scores for previous 5 home/away games
        game_at_home = p_stats[p_id][season][week]['home']
        home_away_scores = [p_scores[p_id][s][w] for s in p_scores[p_id] for w in p_scores[p_id][s] \
                  if s <= season and (w < week or s < season) and p_scores[p_id][s][w] is not None \
                  and p_stats[p_id][s][w]['home'] == game_at_home]
        home_away_scores = [0 for i in range(5-len(home_away_scores))] + home_away_scores
        # phi += home_away_scores[-5:]
        # scores for previous 3 games vs. opponent
        player_team = p_info[p_id][1]
        if team_o[player_team][season][week]:
        	opponent = team_o[player_team][season][week]['opp']
        else:
        	opponent = None
        vs_opp_scores = [p_scores[p_id][s][w] for s in p_scores[p_id] for w in p_scores[p_id][s] \
                  if s <= season and (w < week or s < season) and p_scores[p_id][s][w] is not None \
                  and team_o[player_team][s][w] is not None and team_o[player_team][s][w]['opp'] == opponent]
        vs_opp_scores = [0 for i in range(3-len(vs_opp_scores))] + vs_opp_scores
        phi += vs_opp_scores[-3:]

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
