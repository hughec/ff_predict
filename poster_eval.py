import oracle_data as oracle
import read_nfl as rn
import baseline
import regression as reg
import operator

#Top Players
p_info = [('00-0029668', ('A.Luck', 'IND', 'QB')),('00-0027656', ('R.Gronkowski', 'NE', 'TE')),\
          ('00-0027793', ('A.Brown', 'PIT', 'WR')),('00-0028009', ('D.Murray', 'DAL', 'RB'))]

#Evaluation code
# team data 2010-2014
team_o, team_d = rn.read_team_data()

#Get score for each week
for i in range(1,14):
    train_info, train_scores, train_stats = rn.read_player_data(seasons=[2010,2011,2012,2013,2014],weeks=range(1,i))
    #Train the linear regression classifier
    X, y = reg.extract_features(train_info, train_scores, train_stats, team_o, team_d)
    regr = reg.train_regression(X,y)
    #Test data
    test_info, test_scores, test_stats = rn.read_player_data(seasons=range(2010,2015))
    for player in p_info:
        print player,i
        p_id = player[0]
        o = oracle.get_oracle_data(player[1],2014,i)
        actual = test_scores[p_id][2014][i]
        b = baseline.season_average_predict(train_scores[p_id][2014],i)
        phi = reg.build_phi(test_info, test_scores, test_stats, team_o, team_d, p_id, 2014, i)
        r = regr.predict(phi)
        print actual,",",o,",",b,",",r
