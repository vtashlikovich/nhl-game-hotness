from functools import reduce
from .stars import STARS
import itertools

LEVEL_HOT = 16
LEVEL_WOW = 30

POINTS_OT = "OT"
POINTS_SO = "SO"
POINTS_LONG_SO = "LSO"
POINTS_LONG_SO_EXTRA = "LSOE"
POINTS_TIGHT_FIGHT = "TightFight"
POINTS_WALL = "Wall"
POINTS_HIGH_TENSION = "HighTension"
POINTS_LAST_CHANCE = "LChance"
POINTS_LAST_CHANCE20 = "LChance20"
POINTS_LAST_CHANCE5 = "LChance5"
POINTS_LATE_WINNER = "LateWinner"
POINTS_TIGHT_WIN = "TightWin"
POINTS_LATE_TIGHT_WIN = "LateTightWin"
POINTS_LATE_TIGHT_WIN20 = "LateTightWin20"
POINTS_COME_BACK = "ComeBack"
POINTS_EQUAL_GAME = "EqualG"
POINTS_EQUAL_GAME3 = "EqualG3"
POINTS_MISSED_CHANCE = "MChance"
POINTS_HAT_TRICK = "Hat"
POINTS_POKER = "Poker"
POINTS_MAD_SCORER = "Mad"
POINTS_STAR_POINTS = "SPoints"
POINTS_STAR_SHINES = "SShines"
POINTS_MASTER = "PMaster"

ALL_POINTS = {
    POINTS_OT: 6,
    POINTS_SO: 4,
    POINTS_LONG_SO: 3,
    POINTS_LONG_SO_EXTRA: 3,
    POINTS_TIGHT_FIGHT: 8,
    POINTS_WALL: 8,
    POINTS_HIGH_TENSION: 8,
    POINTS_LAST_CHANCE: 4,
    POINTS_LAST_CHANCE20: 6,
    POINTS_LAST_CHANCE5: 8,
    POINTS_LATE_WINNER: 6,
    POINTS_TIGHT_WIN: 8,
    POINTS_LATE_TIGHT_WIN: 4,
    POINTS_LATE_TIGHT_WIN20: 6,
    POINTS_COME_BACK: 8,
    POINTS_EQUAL_GAME: 5,
    POINTS_EQUAL_GAME3: 8,
    POINTS_MISSED_CHANCE: 4,
    POINTS_HAT_TRICK: 4,
    POINTS_POKER: 7,
    POINTS_MAD_SCORER: 20,
    POINTS_STAR_POINTS: 1,
    POINTS_STAR_SHINES: 3,
    POINTS_MASTER: 1,
}


class GameStats:
    def __init__(self, json: dict):
        self.game = json
        self.points = []
        self.points_sum = 0

    def think(self):
        if "liveData" in self.game.keys():
            # OT
            self.findOT()

            # S/O
            self.findSO()

            # Long S/O session
            self.findLongSO()

            # Tight fight, 28+ shots by both teams in regular
            self.findTightFight()

            # The wall, 35+ saves by any goalkeeper in regular
            self.findTheWall()

            # High tension: OT, when regular ends with 4:4+
            self.findHighTension()

            # Last chance, OT set up on the last minute/20/5 seconds of regular
            self.findLastChance()

            # Late winner, Goal on the last 15 seconds of OT
            self.findLateOTWinner()

            # Tight win, both scores 3+, games ends regular with 1 puck difference
            # Late tight win, Tight win and the winning goal with in the last minute of 3rd
            self.findTightWin()

            # Come back, 3+ straight goals, up to even score or advantage
            self.findComeBack()

            # Equal play (1:1, 2:2, 3:3, ..) up to 2/3 times per game
            self.find_equal_gGame()

            # Missed chance, in 3rd period a game no goalkeeper, opponent scores in empty net
            self.findMissedChance()

            noticable_players = self.gatherNoticablePlayers()

            # hat-trick, 3 goals by one player
            # poker, 4 goals by one player
            # 5+ goals by one player, madness
            self.findTricks(noticable_players)

            # Star shines, star player with 1+ goal or 2+ assists or 3+ points
            # Star scores, star player has at least 1 point
            self.findStarShines(noticable_players)

            # Points master, no star players with 3+ points
            self.findPointsMaster(noticable_players)

            # TODO: goal while having own empty net
            # 2021020319

            # TODO: too many goals - 4 points for each 5 goals by 1 team
            # TODO: too many goals - 3 points if team scored >= 7

            # TODO: 1 point for each goal ?

            # TODO: points for lots of penalties

            # TODO: points for no goals while 3 on 5

            # TODO: determine a fight in the game

            # TODO: team with league bottom beats high league team

            # TODO: points for bullit ?

            # TODO: empty net - goal post

            # TODO: points for lots of post/bar shots

            # TODO: goal on the first seconds

            # TODO: shorthanded goals (in minority)

            # TODO: Start goalie shines, star golie with 30+ saves
            # TODO: Gordie Howe hat-trick, 1 goal, 1 assist, 1 fight

            # TODO: if few points - add points if more than 3 pucks are scored in the game
            # homeGoals, awayGoals = self.getRegularItems("goals")

            self.points_sum = sum([x["points"] for x in self.getPoints()])

    def getPoints(self) -> list:
        return self.points

    def isHot(self) -> bool:
        return self.points_sum >= LEVEL_HOT

    def isWow(self) -> bool:
        return self.points_sum >= LEVEL_WOW

    def findOT(self):
        if (
            self.game["liveData"]["linescore"]["currentPeriodOrdinal"] in ["OT", "SO"]
            and self.game["liveData"]["linescore"]["currentPeriodTimeRemaining"]
            == "Final"
        ):
            self.add_score(POINTS_OT)

    def findSO(self):
        if (
            self.game["liveData"]["linescore"]["currentPeriodOrdinal"] == "SO"
            and self.game["liveData"]["linescore"]["currentPeriodTimeRemaining"]
            == "Final"
        ):
            self.add_score(POINTS_SO)

    def findLongSO(self):
        if (
            self.game["liveData"]["linescore"]["currentPeriodOrdinal"] == "SO"
            and self.game["liveData"]["linescore"]["currentPeriodTimeRemaining"]
            == "Final"
            and self.game["liveData"]["linescore"]["shootoutInfo"]["home"]["attempts"]
            > 3
        ):
            if (
                self.game["liveData"]["linescore"]["shootoutInfo"]["home"]["attempts"]
                > 7
            ):
                self.add_score(POINTS_LONG_SO_EXTRA)
            else:
                self.add_score(POINTS_LONG_SO)

    def getRegularIterators(self):
        iterHome, iterAway = itertools.tee(
            filter(
                lambda x: x["periodType"] == "REGULAR",
                self.game["liveData"]["linescore"]["periods"],
            )
        )
        return (iterHome, iterAway)

    def getRegularItems(self, item_name):
        iter_home, iter_away = self.getRegularIterators()
        home_items = sum([x["home"][item_name] for x in iter_home])
        away_items = sum([x["away"][item_name] for x in iter_away])
        return (home_items, away_items)

    # Tight fight, 28+ shots by both teams in regular
    def findTightFight(self):
        home_shots, away_shots = self.getRegularItems("shotsOnGoal")

        if home_shots > 27 and away_shots > 27:
            self.add_score(POINTS_TIGHT_FIGHT)

    # The wall, 35+ saves by any goalkeeper in regular
    def findTheWall(self):
        home_shots, away_shots = self.getRegularItems("shotsOnGoal")
        home_goals, away_goals = self.getRegularItems("goals")

        away_goalie_saves = home_shots - home_goals
        home_goalie_saves = away_shots - away_goals

        if away_goalie_saves > 34 or home_goalie_saves > 34:
            self.add_score(POINTS_WALL)

    def findHighTension(self):
        home_regular_goals, away_regular_goals = self.getRegularItems("goals")

        if (
            self.game["liveData"]["linescore"]["currentPeriodOrdinal"] in ["OT", "SO"]
            and home_regular_goals > 3
            and away_regular_goals > 3
        ):
            self.add_score(POINTS_HIGH_TENSION)

    def getAllPeriodGoals(self, period_name):
        # loop and collect all goals of the period
        target_period = None
        if period_name == "REGULAR":
            target_period = filter(
                lambda x: x["about"]["periodType"] == period_name
                and x["about"]["ordinalNum"] == "3rd"
                and x["result"]["eventTypeId"] == "GOAL",
                self.game["liveData"]["plays"]["allPlays"],
            )
        elif period_name == "OVERTIME":
            target_period = filter(
                lambda x: x["about"]["periodType"] == period_name
                and x["result"]["eventTypeId"] == "GOAL",
                self.game["liveData"]["plays"]["allPlays"],
            )

        return target_period

    # get time left of the last goal before the specified period end
    def getLastGoalLeftTime(self, periodName) -> int:
        time = -1

        target_period = self.getAllPeriodGoals(periodName)

        # collect list of time remaining
        all_goal_left_times = [x["about"]["periodTimeRemaining"] for x in target_period]

        # find tha latest goal - calc time remaining to the end of period
        if len(all_goal_left_times) > 0:
            latGoalTime = all_goal_left_times[-1].split(":")
            if len(latGoalTime) == 2:
                time = int(latGoalTime[0]) * 60 + int(latGoalTime[1])

        return time

    # Last chance, OT set up on the last minute/20/5 seconds of regular
    def findLastChance(self):
        last_goal_left_time = self.getLastGoalLeftTime("REGULAR")
        if (
            self.game["liveData"]["linescore"]["currentPeriodOrdinal"] in ["OT", "SO"]
            and last_goal_left_time != -1
        ):
            if last_goal_left_time < 6:
                self.add_score(POINTS_LAST_CHANCE5)
            elif last_goal_left_time < 21:
                self.add_score(POINTS_LAST_CHANCE20)
            elif last_goal_left_time < 61:
                self.add_score(POINTS_LAST_CHANCE)


    # Late winner, Goal on the last 15 seconds of OT
    def findLateOTWinner(self):
        last_goal_left_time = self.getLastGoalLeftTime("OVERTIME")
        if (
            self.game["liveData"]["linescore"]["currentPeriodOrdinal"] == "OT"
            and last_goal_left_time != -1
            and last_goal_left_time < 16
        ):
            self.add_score(POINTS_LATE_WINNER)

    # Tight win, both scores 3+, games ends regular with 1 puck difference
    def findTightWin(self):
        home_goals = self.game["liveData"]["linescore"]["teams"]["home"]["goals"]
        away_goals = self.game["liveData"]["linescore"]["teams"]["away"]["goals"]
        if (
            self.game["liveData"]["linescore"]["currentPeriodOrdinal"] == "3rd"
            and self.game["liveData"]["linescore"]["currentPeriodTimeRemaining"]
            == "Final"
            and home_goals > 2
            and away_goals > 2
            and abs(home_goals - away_goals) == 1
        ):
            self.add_score(POINTS_TIGHT_WIN)

            # get the last goal time left
            last_goal_left_time = self.getLastGoalLeftTime("REGULAR")

            # determine if it's a winning goal
            target_period = list(self.getAllPeriodGoals("REGULAR"))
            winning_goal = False
            if len(target_period) > 0:
                winning_goal = target_period[-1]["result"]["gameWinningGoal"]

            if (
                winning_goal
                and self.game["liveData"]["linescore"]["currentPeriodOrdinal"] == "3rd"
                and last_goal_left_time != -1
            ):
                if last_goal_left_time < 21:
                    self.add_score(POINTS_LATE_TIGHT_WIN20)
                elif last_goal_left_time < 61:
                    self.add_score(POINTS_LATE_TIGHT_WIN)

    def get_regular_goals(self) -> list:
        all_regular_goals = filter(
            lambda x: x["about"]["periodType"] == "REGULAR"
            and x["result"]["eventTypeId"] == "GOAL",
            self.game["liveData"]["plays"]["allPlays"],
        )

        return [x["about"]["goals"] for x in all_regular_goals]

    # Come back, 3+ straight goals, up to equal score or advantage (opponent scores 3+)
    def findComeBack(self):
        all_regular_goals = self.get_regular_goals()

        last_home, lastAway = 0, 0
        last_scorer = "none"
        last_home_seq, last_away_seq = 0, 0
        last_score = {"home": 0, "away": 0}
        for item in all_regular_goals:
            # print(item)
            cur_scorer = "none"
            if item["home"] > last_home:
                cur_scorer = "home"
            else:
                cur_scorer = "away"

            if cur_scorer == last_scorer:
                if cur_scorer == "home":
                    last_home_seq += 1
                else:
                    last_away_seq += 1
            else:
                # check if goal has been hit
                if (
                    last_home_seq > 2
                    and last_score["away"] > 2
                    and item["home"] - item["away"] >= 0
                ):
                    self.add_score(POINTS_COME_BACK)
                if (
                    last_away_seq > 2
                    and last_score["home"] > 2
                    and item["away"] - item["home"] >= 0
                ):
                    self.add_score(POINTS_COME_BACK)

                last_home_seq, last_away_seq = 0, 0
                if cur_scorer == "home":
                    last_home_seq = 1
                else:
                    last_away_seq = 1

            # print(curScorer, lastAwaySeq, lastHomeSeq)

            last_home, lastAway = item["home"], item["away"]
            last_scorer = cur_scorer
            last_score = item

        if (
            last_home_seq > 2
            and last_score["away"] > 2
            and last_score["home"] - last_score["away"] >= 0
        ):
            self.add_score(POINTS_COME_BACK)
        if (
            last_away_seq > 2
            and last_score["home"] > 2
            and last_score["away"] - last_score["home"] >= 0
        ):
            self.add_score(POINTS_COME_BACK)

    # Equal play up to 3:3, e.g.: 1:0, 1:1, 2:1, 2:2, 3:2, 3:3, ...
    def find_equal_gGame(self):
        all_regular_goals = self.get_regular_goals()

        equal_game_counter = 0
        for item in all_regular_goals:
            if item["home"] == item["away"]:
                equal_game_counter += 1

        if equal_game_counter == 2:
            self.add_score(POINTS_EQUAL_GAME)
        elif equal_game_counter > 2:
            self.add_score(POINTS_EQUAL_GAME3)

    # Missed chance, in 3rd period a game no goalkeeper, opponent scores in empty net
    def findMissedChance(self):
        all_regular_3rd_goals = filter(
            lambda x: x["about"]["periodType"] == "REGULAR"
            and x["about"]["ordinalNum"] == "3rd"
            and x["result"]["eventTypeId"] == "GOAL"
            and x["result"]["emptyNet"],
            self.game["liveData"]["plays"]["allPlays"],
        )

        if len(list(all_regular_3rd_goals)) > 0:
            self.add_score(POINTS_MISSED_CHANCE)

    def gatherNoticablePlayers(self) -> list:
        away_players = list(
            filter(
                lambda x: x["position"]["code"] != "G"
                and "skaterStats" in x["stats"]
                and (
                    x["stats"]["skaterStats"]["goals"] > 0
                    or x["stats"]["skaterStats"]["assists"] > 0
                ),
                self.game["liveData"]["boxscore"]["teams"]["away"]["players"].values(),
            )
        )

        home_players = list(
            filter(
                lambda x: x["position"]["code"] != "G"
                and "skaterStats" in x["stats"]
                and (
                    x["stats"]["skaterStats"]["goals"] > 0
                    or x["stats"]["skaterStats"]["assists"] > 0
                ),
                self.game["liveData"]["boxscore"]["teams"]["home"]["players"].values(),
            )
        )

        return [
            {
                "id": x["person"]["id"],
                "goals": x["stats"]["skaterStats"]["goals"],
                "assists": x["stats"]["skaterStats"]["assists"],
            }
            for x in away_players + home_players
        ]

    # hat-trick, 3 goals by one player
    # poker trick, 4 goals by one player
    # 5+ goals by one player
    def findTricks(self, noticable_players):
        hat_tricks = len(list(filter(lambda x: x["goals"] == 3, noticable_players)))
        poker_tricks = len(list(filter(lambda x: x["goals"] == 4, noticable_players)))
        more_tricks = len(list(filter(lambda x: x["goals"] > 4, noticable_players)))
        if hat_tricks > 0:
            self.add_score(POINTS_HAT_TRICK, hat_tricks)
        if poker_tricks > 0:
            self.add_score(POINTS_POKER, poker_tricks)
        if more_tricks > 0:
            self.add_score(POINTS_MAD_SCORER)

    # Star shines / Star has points, 1+ goal Or 2+ assists, 3+ points by any star
    def findStarShines(self, noticable_players):
        star_shines_count = 0
        star_has_points = 0
        for player in noticable_players:
            if player["id"] in STARS:
                star_has_points += 1

                if (
                    player["goals"] > 0
                    or player["assists"] > 1
                    or (player["goals"] + player["assists"]) > 2
                ):
                    star_shines_count += 1
                    star_has_points -= 1

        if star_has_points > 0:
            self.add_score(POINTS_STAR_POINTS)

        if star_shines_count > 0:
            self.add_score(POINTS_STAR_SHINES)

    # Points master, no star players with 3+ points
    def findPointsMaster(self, noticable_players):
        players_with_big_points = 0
        for player in noticable_players:
            if player not in STARS and (player["goals"] + player["assists"]) > 2:
                players_with_big_points += 1

        if players_with_big_points > 0:
            self.add_score(POINTS_MASTER, players_with_big_points)

    def add_score(self, score_type: str, score_multiplicator: int = 1):
        self.points.append(
            {"code": score_type, "points": ALL_POINTS[score_type] * score_multiplicator}
        )
