#!/usr/bin/env python

import requests, json, sys
from datetime import datetime, timedelta
from gamestats import GameStats

JIRA_API_URL = "https://statsapi.web.nhl.com/api/v1/"

if len(sys.argv) > 1:
    gameId = sys.argv[1]
else:
    print("gameId is needed")
    exit(1)

print("Check game " + gameId + " hotness")

gameResponse = requests.get(
    JIRA_API_URL + "game/" + str(gameId) + "/feed/live",
    params={"Content-Type": "application/json"},
)

if gameResponse is not None:
    analyzer = GameStats(gameResponse.json())
    analyzer.think()

    gamePoints = sum([x["points"] for x in analyzer.getPoints()])

    print(
        gameId,
        str(gamePoints)
    )

    print(analyzer.getPoints())
