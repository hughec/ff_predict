import urllib2
import re

#Takes a player info card {name, team, position}, year and week
#and returns the fantasy prediction from fftoday.com
def get_oracle_data(player_info,year,week):
    #Constants
    YAHOO_LEAGUE_ID = 17
    POSITION_ID = {"QB": 10, "RB": 20, "WR": 30, "TE": 40}
    #Build url
    url = "http://www.fftoday.com/rankings/playerwkproj.php?Season={}&GameWeek={}&PosID={}&LeagueID={}".format(year,week,POSITION_ID[player_info[2]],YAHOO_LEAGUE_ID)
    #Download the page
    response = urllib2.urlopen(url)
    html = response.read()
    #Process the table entry with the regex
    regex = ">"+player_info[0]+".+?(\d+\.?[\d+]?)</TD>\n</TR>"
    proj = re.search(regex, html, flags=re.S)
    if proj is None:
        return None:
    else:
        return proj.groups(0)[0]
