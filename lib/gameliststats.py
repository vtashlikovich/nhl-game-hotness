import requests, json, sys, logging
from datetime import datetime, timedelta
from .gamestats import GameStats
import traceback

NHL_API_URL = "https://statsapi.web.nhl.com/api/v1/"

class GameListStats:

    def __init__(self, start_date: str = None, end_date: str = None, logger = None):
        self.logger = logger
        self.results = []
        self.start_date = start_date
        self.end_date = end_date

        today = datetime.now()

        if start_date is None:
            earlier3days = today - timedelta(days=3)
            self.start_date = earlier3days.strftime("%Y-%m-%d")

        if end_date is None:
            self.end_date = today.strftime("%Y-%m-%d")

    def think(self, log_live_result: bool = False):
        self.logger.info(f'{self.start_date=}, {self.end_date=}')
        URL = NHL_API_URL + "schedule?startDate=" + self.start_date + "&endDate=" + self.end_date

        if (self.logger is not None):
            self.logger.info("getting list: " + URL)

        try:
            list_response = requests.get(URL, params={"Content-Type": "application/json"})

            if list_response is not None:
                list_json = list_response.json()

                if (self.logger is not None):
                    self.logger.info("parsing each game")

                for date_item in list_json["dates"]:
                    game_date = date_item["date"]

                    if (self.logger is not None):
                        self.logger.info("date: " + game_date)

                    for game_item in filter(
                        lambda x: x["status"]["detailedState"] == "Final"
                        and x["status"]["abstractGameState"] == "Final",
                        date_item["games"],
                    ):
                        game_id = game_item["gamePk"]

                        home_team = {
                            "id": game_item["teams"]["home"]["team"]["id"],
                            "name": game_item["teams"]["home"]["team"]["name"],
                        }

                        away_team = {
                            "id": game_item["teams"]["away"]["team"]["id"],
                            "name": game_item["teams"]["away"]["team"]["name"],
                        }

                        game_URL = NHL_API_URL + "game/" + str(game_id) + "/feed/live"

                        if (self.logger is not None):
                            self.logger.info("checking game: " + str(game_id))

                        game_response = requests.get(
                            game_URL,
                            params={"Content-Type": "application/json"},
                        )

                        if game_response is not None:
                            analyzer = GameStats(game_response.json())
                            analyzer.think()

                            game_points = sum([x["points"] for x in analyzer.getPoints()])

                            hottness_level = ""
                            if analyzer.isWow(): hottness_level = "WOW!"
                            elif analyzer.isHot(): hottness_level = "HOT"

                            self.results.append({
                                "date": game_date,
                                "id": game_id,
                                "awayteam": away_team["name"],
                                "awayabr": analyzer.game["gameData"]["teams"]["away"]["abbreviation"],
                                "hometeam": home_team["name"],
                                "homeabr": analyzer.game["gameData"]["teams"]["home"]["abbreviation"],
                                "points": game_points,
                                "hottness": hottness_level
                            })

                            if log_live_result:
                                print(
                                    game_date + ",",
                                    str(game_id) + ",",
                                    (away_team["name"]
                                    + " / "
                                    + home_team["name"] + ",").ljust(50),
                                    str(game_points).ljust(3),
                                    hottness_level
                                )

                if (self.logger is not None):
                    self.logger.info("success")

        except Exception as exc:
            traceback_info = sys.exc_info()
            print(f"Exception occured: {type(exc).__name__}, {traceback_info}")
            traceback.print_tb(exc.__traceback__)
            self.logger.critical(f"Exception occured: {type(exc).__name__}, {traceback_info}")