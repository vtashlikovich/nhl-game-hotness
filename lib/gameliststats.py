import requests
import sys
from datetime import datetime, timedelta
from .gamestats import GameStats
import traceback

NHL_API_URL = 'https://api-web.nhle.com/v1/'


class GameListStats:

    def __init__(self, start_date: str = None, end_date: str = None, logger=None):
        self.logger = logger
        self.results = []
        self.start_date = start_date
        self.end_date = end_date
        self.req = requests.Session()

        today = datetime.now()

        if start_date is None:
            earlier3days = today - timedelta(days=3)
            self.start_date = earlier3days.strftime('%Y-%m-%d')

        if end_date is None:
            self.end_date = today.strftime('%Y-%m-%d')

    def think(self, log_live_result: bool = False):
        self.logger.info(f'{self.start_date=}, {self.end_date=}')
        URL = NHL_API_URL + 'schedule/' + self.start_date

        if (self.logger is not None):
            self.logger.info('getting list: ' + URL)

        try:
            list_response = self.req.get(URL, params={'Content-Type': 'application/json'})

            if list_response is not None:
                list_json = list_response.json()

                if (self.logger is not None):
                    self.logger.info('parsing each game')

                for date_item in list_json['gameWeek']:
                    # game_date = date_item['date']
                    game_date = date_item['date']

                    if (self.logger is not None):
                        self.logger.info('date: ' + game_date)

                    for game_item in filter(
                        lambda x: x['gameState'] == 'OFF',
                        date_item['games']
                    ):
                        game_id = game_item['id']

                        home_team = {
                            'id': game_item['homeTeam']['id'],
                            'name': game_item['homeTeam']['abbrev'],
                        }

                        away_team = {
                            'id': game_item['awayTeam']['id'],
                            'name': game_item['awayTeam']['abbrev'],
                        }

                        playbyplay_URL = f'{NHL_API_URL}gamecenter/{game_id}/play-by-play'
                        boxscore_URL = f'{NHL_API_URL}gamecenter/{game_id}/boxscore'

                        if (self.logger is not None):
                            self.logger.info('checking game: ' + str(game_id))

                        playbyplay_response = self.req.get(
                            playbyplay_URL,
                            params={'Content-Type': 'application/json'},
                        )

                        boxscore_response = self.req.get(
                            boxscore_URL,
                            params={'Content-Type': 'application/json'},
                        )

                        if playbyplay_response is not None and boxscore_response is not None:
                            analyzer = GameStats(playbyplay_response.json(), boxscore_response.json())
                            analyzer.think()

                            game_points = sum([x['points'] for x in analyzer.getPoints()])

                            hottness_level = ''
                            if analyzer.isWow(): hottness_level = 'WOW!'
                            elif analyzer.isHot(): hottness_level = 'HOT'

                            away_team_name = analyzer.game["awayTeam"]["name"]["default"]
                            home_team_name = analyzer.game["homeTeam"]["name"]["default"]

                            self.results.append({
                                "date": game_date,
                                "id": game_id,
                                "awayteam": away_team_name,
                                "awayabr": analyzer.game["awayTeam"]["abbrev"],
                                "hometeam": home_team_name,
                                "homeabr": analyzer.game["homeTeam"]["abbrev"],
                                "points": game_points,
                                "hottness": hottness_level
                            })

                            if log_live_result:
                                print(
                                    game_date + ',',
                                    str(game_id) + ',',
                                    (away_team_name + ' / ' + home_team_name + ',').ljust(50),
                                    str(game_points).ljust(3),
                                    hottness_level
                                )

                if (self.logger is not None):
                    self.logger.info('success')

        except Exception as exc:
            traceback_info = sys.exc_info()
            print(f'Exception occured: {type(exc).__name__}, {traceback_info}')
            traceback.print_tb(exc.__traceback__)
            self.logger.critical(f'Exception occured: {type(exc).__name__}, {traceback_info}')
