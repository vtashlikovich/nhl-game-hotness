import requests
import json
from gamestats import GameStats

# TODO: Grab game ID from argument
# gameId = '2021020176'

# URL = 'https://statsapi.web.nhl.com/api/v1/game/' + gameId + '/feed/live'
# response = requests.get(
#     URL, params={"Content-Type": "application/json"}
# )

# gameJson = response.json()
# print(len(gameJson))

# if response is not None:
#     # print(json['liveData']['plays']['allPlays'])
#     print('events:', len(gameJson['liveData']['plays']['allPlays']))

fileName = 'live_curl-REGULAR.json'
# fileName = 'live_curl_OT.json'
# fileName = 'live_curl_SO.json'

with open('docs/samples/' + fileName) as f:
    gameJson = json.load(f)

    analyzer = GameStats(gameJson)
    analyzer.think()

    print(analyzer.getPoints())

    gamePoints = sum(list(map(lambda x: x["points"], analyzer.getPoints())))

    print('gamePoints:', gamePoints)