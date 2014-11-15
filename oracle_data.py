import urllib2
import re

#Takes a player info card {name, team, position}, year and week
#and returns the fantasy prediction from fftoday.com
cache = {}
def get_oracle_data(player_info,year,week):
    #Constants
    YAHOO_LEAGUE_ID = 17
    POSITION_ID = {"QB": 10, "RB": 20, "WR": 30, "TE": 40, "FB": 20}
    if player_info[2] == '':
        position_codes = [10,20,30,40]
    else:
        position_codes = [POSITION_ID[player_info[2]]]
    for code in position_codes:
        html = get_html(year,week,code,YAHOO_LEAGUE_ID)
        #Process the table entry with the regex
        regex = ">"+player_info[0][0]+"\S+ "+player_info[0][2:]+".+?(\d+\.?[\d+]?)</TD>\n</TR>"
        proj = re.search(regex, html, flags=re.S)
        if proj is not None:
            return proj.groups(0)[0]
    #No match found
    return None

def get_html(year,week,code,leagueID):
    if (year,week,code,leagueID) not in cache:
        #Build url
        url = "http://www.fftoday.com/rankings/playerwkproj.php?Season={}&GameWeek={}&PosID={}&LeagueID={}".format(year,week,code,leagueID)
        #Download the page
        response = urllib2.urlopen(url)
        cache[year,week,code,leagueID] = response.read()
    return cache[year,week,code,leagueID]        
