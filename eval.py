import oracle_data as oracle
import read_nfl as rn
import baseline
import regression as reg
import operator

#Get list of eligible players return list of tuples: (id,(player_name, team, position))
def get_top_players(player_info, player_scores, n):
    sorted_players = sorted(player_info.items(), key=lambda x: -sum([0 if v2 is None else v2 for k,v in player_scores[x[0]].iteritems() for k2,v2 in v.iteritems()]))
    return {sorted_players[i][0]: sorted_players[i][1] for i in range(n)}

#Calculate baseline, oracle and regression error for a given data set and regression
#Only looks at weeks 2-17 so it can use season average
def get_errors(p_info, p_scores, p_stats, team_o, team_d, regr):
    baseline_error = 0.0
    oracle_error = 0.0
    reg_error = 0.0
    sample_count = 0
    for p_id in p_info:
        if p_id not in p_scores:
            continue
        for season in p_scores[p_id]:
            p_weeks = p_scores[p_id][season]
            for week in range(2,18):
                if p_weeks[week] is not None:
                    o = oracle.get_oracle_data(p_info[p_id],season,week)
                    actual = p_scores[p_id][season][week]
                    if o is not None and actual is not None:
                        oracle_error += (float(o) - actual) ** 2
                        b = baseline.season_average_predict(p_weeks,week)
                        baseline_error += (float(b) - actual) ** 2
                        phi = reg.build_phi(p_info, p_scores, p_stats, team_o, team_d, p_id, season, week)
                        r = regr.predict(phi)
                        reg_error += (float(r) - actual) **2
                        sample_count +=1

    print "Oracle error: ",oracle_error/sample_count
    print "Baseline error: ",baseline_error/sample_count
    print "Regression error: ",reg_error/sample_count

#Evaluation code
#Get the top n players
n=200

# team data 2010-2014
team_o, team_d = rn.read_team_data()

#Training data 2010-2013
train_info, train_scores, train_stats = rn.read_player_data(seasons=[2010,2011,2012,2013])
top_player_info = get_top_players(train_info, train_scores,n)

#Test data 2014
test_info, test_scores, test_stats = rn.read_player_data(seasons=[2014])

#Train the linear regression classifier
X, y = reg.extract_features(train_info, train_scores, train_stats, team_o, team_d)
regr = reg.train_regression(X,y)

#Calculate training error
print "Training Error"
get_errors(top_player_info,train_scores, train_stats, team_o, team_d, regr)

#Calculate test error
print "Test Error"
get_errors(top_player_info,test_scores, test_stats, team_o, team_d, regr)