#!/usr/bin/env python

import requests
import sys
from lib.gamestats import GameStats

NHL_API_URL = "https://api-web.nhle.com/v1/"

if len(sys.argv) > 1:
    game_id = str(sys.argv[1])
else:
    print("game_id is needed")
    exit(1)

print("Check game " + game_id + " hotness")

try:
    playbyplay_URL = f"{NHL_API_URL}gamecenter/{game_id}/play-by-play"
    boxscore_URL = f"{NHL_API_URL}gamecenter/{game_id}/boxscore"

    playbyplay_response = requests.get(
        playbyplay_URL,
        params={"Content-Type": "application/json"},
    )

    boxscore_response = requests.get(
        boxscore_URL,
        params={"Content-Type": "application/json"},
    )

    if playbyplay_response is not None and boxscore_response is not None:
        analyzer = GameStats(playbyplay_response.json(), boxscore_response.json())
        analyzer.think()

        gamePoints = sum([x["points"] for x in analyzer.get_points()])

        print(game_id, str(gamePoints))

        print(analyzer.get_points())

except Exception as exc:
    traceback = sys.exc_info()
    print("Exception occured", type(exc).__name__, traceback)
