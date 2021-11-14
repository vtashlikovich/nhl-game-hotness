import requests
import json
from gamestats import GameStats

baseURL = "https://statsapi.web.nhl.com/api/v1/"

URL = baseURL + "schedule?startDate=2021-11-12&endDate=2021-11-14"
listResponse = requests.get(
    URL, params={"Content-Type": "application/json"}
)

if listResponse is not None:
    listJson = listResponse.json()

    for dateItem in listJson["dates"]:
        gameDate = dateItem["date"]
        
        for gameItem in filter(lambda x: x["status"]["detailedState"] == "Final" \
            and x["status"]["abstractGameState"] == "Final", dateItem["games"]):
            gameId = gameItem["gamePk"]

            homeTeam = {
                "id": gameItem["teams"]["home"]["team"]["id"],
                "name": gameItem["teams"]["home"]["team"]["name"],
            }

            awayTeam = {
                "id": gameItem["teams"]["away"]["team"]["id"],
                "name": gameItem["teams"]["away"]["team"]["name"],
            }

            gameResponse = requests.get(
                baseURL + "game/" + str(gameId) + "/feed/live", params={"Content-Type": "application/json"}
            )

            if gameResponse is not None:
                analyzer = GameStats(gameResponse.json())
                analyzer.think()

                gamePoints = sum([x["points"] for x in analyzer.getPoints()])
                
                print(gameId, awayTeam["name"] + " / " + homeTeam["name"] + " / " + str(gamePoints))