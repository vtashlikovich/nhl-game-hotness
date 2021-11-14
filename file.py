import requests
import json
from gamestats import GameStats

fileName = 'live_curl-REGULAR.json'
# fileName = 'live_curl_OT.json'
# fileName = 'live_curl_SO.json'

with open('docs/samples/' + fileName) as f:
    gameJson = json.load(f)

    analyzer = GameStats(gameJson)
    analyzer.think()

    print(analyzer.getPoints())

    gamePoints = sum([x["points"] for x in analyzer.getPoints()])

    print('gamePoints:', gamePoints)