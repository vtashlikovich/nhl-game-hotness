import requests, json, sys, logging
from datetime import datetime, timedelta
from .gamestats import GameStats

JIRA_API_URL = "https://statsapi.web.nhl.com/api/v1/"

class GameListStats:

    def __init__(self, startDate: str = None, endDate: str = None, logger = None):
        self.logger = logger
        self.results = []
        self.startDate = startDate
        self.endDate = endDate

        today = datetime.now()

        if startDate is None:
            earlier3days = today - timedelta(days=3)
            self.startDate = earlier3days.strftime("%Y-%m-%d")
        
        if endDate is None:
            self.endDate = today.strftime("%Y-%m-%d")

    def think(self, logLiveResult: bool = False):
        URL = JIRA_API_URL + "schedule?startDate=" + self.startDate + "&endDate=" + self.endDate

        if (self.logger is not None):
            self.logger.info("getting list: " + URL)

        try:
            listResponse = requests.get(URL, params={"Content-Type": "application/json"})

            if listResponse is not None:
                listJson = listResponse.json()

                if (self.logger is not None):
                    self.logger.info("parsing each game")

                for dateItem in listJson["dates"]:
                    gameDate = dateItem["date"]

                    if (self.logger is not None):
                        self.logger.info("date: " + gameDate)

                    for gameItem in filter(
                        lambda x: x["status"]["detailedState"] == "Final"
                        and x["status"]["abstractGameState"] == "Final",
                        dateItem["games"],
                    ):
                        gameId = gameItem["gamePk"]

                        homeTeam = {
                            "id": gameItem["teams"]["home"]["team"]["id"],
                            "name": gameItem["teams"]["home"]["team"]["name"],
                        }

                        awayTeam = {
                            "id": gameItem["teams"]["away"]["team"]["id"],
                            "name": gameItem["teams"]["away"]["team"]["name"],
                        }

                        gameURL = JIRA_API_URL + "game/" + str(gameId) + "/feed/live"
                        
                        if (self.logger is not None):
                            self.logger.info("checking game: " + str(gameId))

                        gameResponse = requests.get(
                            gameURL,
                            params={"Content-Type": "application/json"},
                        )

                        if gameResponse is not None:
                            analyzer = GameStats(gameResponse.json())
                            analyzer.think()

                            gamePoints = sum([x["points"] for x in analyzer.getPoints()])

                            hottnessLevel = ""
                            if analyzer.isWow(): hottnessLevel = "WOW!"
                            elif analyzer.isHot(): hottnessLevel = "HOT"

                            self.results.append({
                                "date": gameDate,
                                "id": gameId,
                                "awayteam": awayTeam["name"],
                                "awayabr": analyzer.game["gameData"]["teams"]["away"]["abbreviation"],
                                "hometeam": homeTeam["name"],
                                "homeabr": analyzer.game["gameData"]["teams"]["home"]["abbreviation"],
                                "points": gamePoints,
                                "hottness": hottnessLevel
                            })

                            if logLiveResult:
                                print(
                                    gameDate + ",",
                                    str(gameId) + ",",
                                    (awayTeam["name"]
                                    + " / "
                                    + homeTeam["name"] + ",").ljust(50),
                                    str(gamePoints).ljust(3),
                                    hottnessLevel
                                )

                if (self.logger is not None):
                    self.logger.info("success")

        except Exception as exc:
            traceback = sys.exc_info()
            print(f"Exception occured: {type(exc).__name__}, {traceback}")
            logger.critical(f"Exception occured: {type(exc).__name__}, {traceback}")