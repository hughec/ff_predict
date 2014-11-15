import oracle_data
import read_nfl
import operator

#Get list of eligible players return list of tuples: (id,(player_name, team, position))
def get_top_players(player_info, player_scores, n):
    sorted_players = sorted(player_info.items(), key=lambda x: -sum(player_scores[x[0]]))
    return [sorted_players[i] for i in range(n)]

#Top 500 players
n=100

player_info, player_scores, player_stats = read_nfl.read_player_data(seasons=range(2013,2014))
top_players = get_top_players(player_info, player_scores,n)

#Evaluate oracle/baseline over weeks 2 to 10
year = 2014
oracle_error = 0.0
baseline_error = 0.0
sample_count = 0
for week in range(2,9):
    for player in top_players:
        oracle = oracle_data.get_oracle_data(player[1],2014,week)
        if oracle is not None and week < len(player_scores[player[0]]):
            actual = player_scores[player[0]][week]
            baseline = read_nfl.decaying_weighted_average_predict(player_scores[player[0]],week-1)
            print player,week,oracle,baseline,actual,float(oracle)-actual,baseline-actual
            oracle_error += (float(oracle) - actual) ** 2
            baseline_error += (baseline - actual) ** 2
            sample_count +=1

print "Baseline:",baseline_error/sample_count
print "Oracle:",oracle_error/sample_count

