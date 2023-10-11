import requests
import xmltodict
from datetime import datetime

def getSeason(year):
    url = "https://ergast.com/api/f1/{}".format(year)
    response = requests.get(url)
    dict = xmltodict.parse(response.content)
    season = {}
    for race in dict['MRData']['RaceTable']['Race']:
        raceStat = {}
        raceStat['round'] = race['@round']
        raceStat['name'] = race['RaceName']
        raceStat['country'] = race['Circuit']['Location']['Country']
        raceStat['date'] = race['Date']
        if 'Sprint' in race:
            raceStat['sprint'] = True
        else:
            raceStat['sprint'] = False
        season[raceStat['round']] = raceStat

    return season


def getChampionship():
    url = "http://ergast.com/api/f1/current/driverStandings"
    response = requests.get(url)
    dict = xmltodict.parse(response.content)
    championship = {}
    
    for driver in dict['MRData']['StandingsTable']['StandingsList']['DriverStanding']:
        racer = {}
        racer['name'] = driver['Driver']['FamilyName']
        racer['team'] = driver['Constructor']['Name']
        racer['points'] = driver['@points']
        championship[driver['@position']] = racer

    return championship

def getRaceResult(year, round):
    url = "http://ergast.com/api/f1/{}/{}/results".format(year, round)
    response = requests.get(url)
    dict = xmltodict.parse(response.content)
    results = {}

    for racer in dict['MRData']['RaceTable']['Race']['ResultsList']['Result']:
        result = {}
        result['name'] = racer['Driver']['@driverId']
        result['points'] = racer['@points']
        if 'FastestLap' in racer:
            result['fastestLapPlace'] = racer['FastestLap']['@rank']
        results[racer['@position']] = result

    return results


season2023 = getSeason(2023)
today = datetime.today()
for round in season2023:
    #If race has been completed
    roundDate = datetime.strptime(season2023[round]['date'], '%Y-%m-%d')
    if today > roundDate:
        raceResult = getRaceResult(2023,round)
        print(raceResult)