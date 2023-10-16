import requests
import xmltodict
import csv
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

def getDrivers(year):
    url = "https://ergast.com/api/f1/{}/drivers".format(year)
    response = requests.get(url)
    dict = xmltodict.parse(response.content)
    drivers = {}
    for driver in dict['MRData']['DriverTable']['Driver']:
        driverInfo = {}
        driverInfo['driverFname'] = driver['GivenName']
        driverInfo['driverLname'] = driver['FamilyName']
        drivers[driver['@driverId']] = driverInfo
    return drivers

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
        result['driverId'] = racer['Driver']['@driverId']
        result['driverFname'] = racer['Driver']['GivenName']
        result['driverLname'] = racer['Driver']['FamilyName']
        result['constructor'] = racer['Constructor']['Name']
        result['place'] = racer['@position']
        result['points'] = racer['@points']
        if 'FastestLap' in racer:
            result['fastestLapPlace'] = racer['FastestLap']['@rank']
        else: 
            result['fastestLapPlace'] = 20
        results[racer['@position']] = result

    return results


def placeToPoints(place, fastestLap):
    match place:
        case '1':
            normalPoints = 25
            pointChange1 = 25
            pointChange2 = 60
        case '2':
            normalPoints = 18
            pointChange1 = 21
            pointChange2 = 50
        case '3':
            normalPoints = 15
            pointChange1 = 18
            pointChange2 = 41
        case '4':
            normalPoints = 12
            pointChange1 = 15
            pointChange2 = 33
        case '5':
            normalPoints = 10
            pointChange1 = 12
            pointChange2 = 26
        case '6':
            normalPoints = 8
            pointChange1 = 10
            pointChange2 = 20
        case '7':
            normalPoints = 6
            pointChange1 = 9
            pointChange2 = 15
        case '8':
            normalPoints = 4
            pointChange1 = 8
            pointChange2 = 11
        case '9':
            normalPoints = 2
            pointChange1 = 7
            pointChange2 = 8
        case '10':
            normalPoints = 1
            pointChange1 = 6
            pointChange2 = 6
        case '11':
            normalPoints = 0
            pointChange1 = 5
            pointChange2 = 5
        case '12':
            normalPoints = 0
            pointChange1 = 4
            pointChange2 = 4
        case '13':
            normalPoints = 0
            pointChange1 = 3
            pointChange2 = 3
        case '14':
            normalPoints = 0
            pointChange1 = 2
            pointChange2 = 2
        case '15':
            normalPoints = 0
            pointChange1 = 1
            pointChange2 = 1
        case _:
            normalPoints = 0
            pointChange1 = 0
            pointChange2 = 0
    if fastestLap == '1' and int(place) <= 10:
        normalPoints = normalPoints + 1
        pointChange1 = pointChange1 + 1
        pointChange2 = pointChange2 + 1
    return [normalPoints, pointChange1, pointChange2]


season2023 = getSeason(2023)
drivers = getDrivers(2023)
today = datetime.today()
results = []
for round in season2023:
    #If race has been completed
    roundDate = datetime.strptime(season2023[round]['date'], '%Y-%m-%d')
    if today > roundDate:
        raceResult = getRaceResult(2023,round)
        results.append(raceResult)

#print(results)

# Get drivers in order with today's points
# Iterate over the results to calculate total points
for round in results:
    for racer in round:
        # Add point data to driver info
        # find driver in the drivers list and add point info
        driverId = round[racer]['driverId']
        thisDriverInfo = drivers[driverId]
        roundPoints = placeToPoints(round[racer]['place'], round[racer]['fastestLapPlace'])
        if 'points' in thisDriverInfo:
            # Points exist so we should add to it
            pastPoints = thisDriverInfo['points']
            newPoints = [pastPoints[0]+roundPoints[0], pastPoints[1]+roundPoints[1], pastPoints[2]+roundPoints[2]]
            thisDriverInfo['points'] = newPoints
        else:
            # First time adding points
            thisDriverInfo['points'] = roundPoints
        drivers[driverId] =thisDriverInfo


# Create print list with details
outputList = []
header = {}
header['Driver'] = 'Driver'
header['Traditional Points'] = 'Traditional Points'
header['Alternative Points Alpha'] = 'Alternative Points Alpha'
header['Alternative Points Beta'] = 'Alternative Points Beta'
outputList.append(header)

for driver in drivers:
    driverInfo = {}
    driverInfo['name'] = (drivers[driver]['driverFname'] + ' ' + drivers[driver]['driverLname'])
    driverInfo['normalPoints'] = (drivers[driver]['points'][0])
    driverInfo['pointChagne1'] = (drivers[driver]['points'][1])
    driverInfo['pointChagne2'] = (drivers[driver]['points'][2])
    outputList.append(driverInfo)


with open('output.csv', 'w', newline='') as csvfile:
  writer = csv.writer(csvfile)
  for row in outputList:
    writer.writerow(row.values())

# Output text file with update time and most recent race/round
updateString = "Last Updated: " + today.isoformat() + ", After Round: " + season2023[str(len(results))]['name']
with open ('lastUpdate.txt', 'w', newline='') as txtfile:
    txtfile.write(updateString)