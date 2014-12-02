import numpy as np

# given a player's fantasy football scores, predicts the player's score in the given week
# based on a decaying weighted average over scores in all previous weeks.
def decaying_weighted_average_predict(scores, week):
	X = scores[:week]
	y = scores[week]
	w = np.arange(1.0 / len(X), 1 + 1.0 / len(X), 1.0 / len(X))
	y_hat = sum([X[i] * w[i] for i in range(len(X))]) / sum(w)
	return y_hat

#Return the season avg score for a given player, scores is a dict of weekly scores
def season_average_predict(scores, week):
        X = [scores[i] for i in range(1,week) if scores[i] is not None]
        return sum(X)/len(X) if len(X) > 0 else 0

#Given a set of player scores returns the MSE using the baseline predictor
def baseline_predictions(p_scores):
	squared_error = []
	for p_id in p_scores:
		scores = [0]
		p_seasons = p_scores[p_id]
		for season in p_seasons:
			p_weeks = p_seasons[season]
			for week in p_weeks:
				if p_weeks[week] is not None:
					scores.append(p_weeks[week])
		if sum(scores) / float(len(scores)) < 5.0: continue
		for week in range(17, len(scores)):
			y = scores[week]
			y_hat = decaying_weighted_average_predict(scores, week)
			squared_error.append((y - y_hat)**2)
	return sum(squared_error) / len(squared_error)
