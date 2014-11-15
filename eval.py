import oracle_data
import read_nfl
import operator

#Get list of eligible players return list of tuples: (id,(player_name, team, position))
def get_top_players(player_info, player_totals, n):
    sorted_players = sorted(player_info.items(), key=lambda x: -player_totals[x[0]])
    return [sorted_players[i] for i in range(n)]

#Top 500 players
n=100

player_info, player_scores, player_totals = read_nfl.read_player_data(seasons=[2013, 2014], weeks=range(1,11))
top_players = get_top_players(player_info, player_totals,n)

top_player_ids = [player[0] for player in top_players]


m = 0
oracle_squared_error = 0.0
baseline_squared_error = 0.0
for player_id in top_player_ids:
    player_name_team_pos = player_info[player_id]
    historical_scores = player_scores[player_id]
    year = 2014
    for week in historical_scores[year]:
        actual_score = historical_scores[year][week]
        oracle_prediction = oracle_data.get_oracle_data(player_name_team_pos, year, week)
        print player_name_team_pos, year, week, actual_score, oracle_prediction
        if oracle_prediction is not None:
            baseline_prediction = read_nfl.decaying_weighted_average_predict(historical_scores, year, week)
            oracle_squared_error += ((actual_score or 0) - float(oracle_prediction))**2
            baseline_squared_error += ((actual_score or 0) - baseline_prediction)**2
            m += 1

#Evaluate oracle/baseline over weeks 2 to 10
# year = 2014
# oracle_error = 0.0
# baseline_error = 0.0
# sample_count = 0
# for week in range(2,9):
#     for player in top_players:
#         oracle = oracle_data.get_oracle_data(player[1],2014,week)
#         if oracle is not None and week < len(player_scores[player[0]]):
#             actual = player_scores[player[0]][week]
#             baseline = read_nfl.decaying_weighted_average_predict(player_scores[player[0]],week-1)
#             print player,week,oracle,baseline,actual,float(oracle)-actual,baseline-actual
#             oracle_error += (float(oracle) - actual) ** 2
#             baseline_error += (baseline - actual) ** 2
#             sample_count +=1

print "Baseline:",baseline_squared_error / m
print "Oracle:",oracle_squared_error/ m

