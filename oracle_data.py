import urllib2
import re
import pickle

#Load cache of downloaded pages
try:
    cache = pickle.load(open("cache.pkl"))
except (IOError,EOFError) as e:
    cache = {}

#Takes a player info card {name, team, position}, year and week
#and returns the fantasy prediction from fftoday.com
def get_oracle_data(player_info,year,week):
    #Constants
    POSITION_ID = {"QB": 10, "RB": 20, "WR": 30, "TE": 40, "FB": 20}
    if player_info[2] not in POSITION_ID:
        position_codes = [10,20,30,40]
    else:
        position_codes = [POSITION_ID[player_info[2]]]
    for code in position_codes:
        for page in [0,1]:
            html = get_html(year,week,code,page)
            #Process the table entry with the regex
            regex = ">"+player_info[0][0]+"\S+ "+player_info[0][2:]+".+?(\d+\.?[\d+]?)</TD>\n</TR>"
            proj = re.search(regex, html, flags=re.S)
            if proj is not None:
                return proj.groups(0)[0]
    #No match found
    return None

def get_html(year,week,pos,page):
    if (year,week,pos,page) not in cache:
        #Build url
        url = "http://www.fftoday.com/rankings/playerwkproj.php?Season={}&GameWeek={}&PosID={}&LeagueID=17&order_by=FFPts&sort_order=DESC&cur_page={}"\
            .format(year,week,pos,page)
        #Download the page
        response = urllib2.urlopen(url)
        cache[year,week,pos,page] = response.read()
        pickle.dump(cache,open("cache.pkl","w"))
    return cache[year,week,pos,page]
