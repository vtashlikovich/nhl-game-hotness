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
        self.pointsSum = 0

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

            noticablePlayers = self.gatherNoticablePlayers()

            # hat-trick, 3 goals by one player
            # poker, 4 goals by one player
            # 5+ goals by one player, madness
            self.findTricks(noticablePlayers)

            # Star shines, star player with 1+ goal or 2+ assists or 3+ points
            # Star scores, star player has at least 1 point
            self.findStarShines(noticablePlayers)

            # Points master, no star players with 3+ points
            self.findPointsMaster(noticablePlayers)

            # TODO: goal while having own empty net
            # 2021020319

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

            self.pointsSum = sum([x["points"] for x in self.getPoints()])

    def getPoints(self) -> list:
        return self.points

    def isHot(self) -> bool:
        return self.pointsSum >= LEVEL_HOT

    def isWow(self) -> bool:
        return self.pointsSum >= LEVEL_WOW

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

    def getRegularItems(self, itemName):
        iterHome, iterAway = self.getRegularIterators()
        homeItems = sum([x["home"][itemName] for x in iterHome])
        awayItems = sum([x["away"][itemName] for x in iterAway])
        return (homeItems, awayItems)

    # Tight fight, 28+ shots by both teams in regular
    def findTightFight(self):
        homeShots, awayShots = self.getRegularItems("shotsOnGoal")

        if homeShots > 27 and awayShots > 27:
            self.add_score(POINTS_TIGHT_FIGHT)

    # The wall, 35+ saves by any goalkeeper in regular
    def findTheWall(self):
        homeShots, awayShots = self.getRegularItems("shotsOnGoal")
        homeGoals, awayGoals = self.getRegularItems("goals")

        awayGoalieSaves = homeShots - homeGoals
        homeGoalieSaves = awayShots - awayGoals

        if awayGoalieSaves > 34 or homeGoalieSaves > 34:
            self.add_score(POINTS_WALL)

    def findHighTension(self):
        homeRegularGoals, awayRegularGoals = self.getRegularItems("goals")

        if (
            self.game["liveData"]["linescore"]["currentPeriodOrdinal"] in ["OT", "SO"]
            and homeRegularGoals > 3
            and awayRegularGoals > 3
        ):
            self.add_score(POINTS_HIGH_TENSION)

    def getAllPeriodGoals(self, periodName):
        # loop and collect all goals of the period
        targetPeriod = None
        if periodName == "REGULAR":
            targetPeriod = filter(
                lambda x: x["about"]["periodType"] == periodName
                and x["about"]["ordinalNum"] == "3rd"
                and x["result"]["eventTypeId"] == "GOAL",
                self.game["liveData"]["plays"]["allPlays"],
            )
        elif periodName == "OVERTIME":
            targetPeriod = filter(
                lambda x: x["about"]["periodType"] == periodName
                and x["result"]["eventTypeId"] == "GOAL",
                self.game["liveData"]["plays"]["allPlays"],
            )
        
        return targetPeriod

    # get time left of the last goal before the specified period end
    def getLastGoalLeftTime(self, periodName) -> int:
        time = -1

        targetPeriod = self.getAllPeriodGoals(periodName)

        # collect list of time remaining
        allGoalLeftTimes = [x["about"]["periodTimeRemaining"] for x in targetPeriod]

        # find tha latest goal - calc time remaining to the end of period
        if len(allGoalLeftTimes) > 0:
            latGoalTime = allGoalLeftTimes[-1].split(":")
            if len(latGoalTime) == 2:
                time = int(latGoalTime[0]) * 60 + int(latGoalTime[1])

        return time

    # Last chance, OT set up on the last minute/20/5 seconds of regular
    def findLastChance(self):
        lastGoalLeftTime = self.getLastGoalLeftTime("REGULAR")
        if (
            self.game["liveData"]["linescore"]["currentPeriodOrdinal"] in ["OT", "SO"]
            and lastGoalLeftTime != -1
        ):
            if lastGoalLeftTime < 6:
                self.add_score(POINTS_LAST_CHANCE5)
            elif lastGoalLeftTime < 21:
                self.add_score(POINTS_LAST_CHANCE20)
            elif lastGoalLeftTime < 61:
                self.add_score(POINTS_LAST_CHANCE)
            

    # Late winner, Goal on the last 15 seconds of OT
    def findLateOTWinner(self):
        lastGoalLeftTime = self.getLastGoalLeftTime("OVERTIME")
        if (
            self.game["liveData"]["linescore"]["currentPeriodOrdinal"] == "OT"
            and lastGoalLeftTime != -1
            and lastGoalLeftTime < 16
        ):
            self.add_score(POINTS_LATE_WINNER)

    # Tight win, both scores 3+, games ends regular with 1 puck difference
    def findTightWin(self):
        homeGoals = self.game["liveData"]["linescore"]["teams"]["home"]["goals"]
        awayGoals = self.game["liveData"]["linescore"]["teams"]["away"]["goals"]
        if (
            self.game["liveData"]["linescore"]["currentPeriodOrdinal"] == "3rd"
            and self.game["liveData"]["linescore"]["currentPeriodTimeRemaining"]
            == "Final"
            and homeGoals > 2
            and awayGoals > 2
            and abs(homeGoals - awayGoals) == 1
        ):
            self.add_score(POINTS_TIGHT_WIN)

            # get the last goal time left
            lastGoalLeftTime = self.getLastGoalLeftTime("REGULAR")

            # determine if it's a winning goal
            targetPeriod = list(self.getAllPeriodGoals("REGULAR"))
            winningGoal = False
            if len(targetPeriod) > 0:
                winningGoal = targetPeriod[-1]["result"]["gameWinningGoal"]

            if (
                winningGoal
                and self.game["liveData"]["linescore"]["currentPeriodOrdinal"] == "3rd"
                and lastGoalLeftTime != -1
            ):
                if lastGoalLeftTime < 21:
                    self.add_score(POINTS_LATE_TIGHT_WIN20)
                elif lastGoalLeftTime < 61:
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
        allRegularGoals = self.get_regular_goals()

        lastHome, lastAway = 0, 0
        lastScorer = "none"
        lastHomeSeq, lastAwaySeq = 0, 0
        lastScore = {"home": 0, "away": 0}
        for item in allRegularGoals:
            # print(item)
            curScorer = "none"
            if item["home"] > lastHome:
                curScorer = "home"
            else:
                curScorer = "away"

            if curScorer == lastScorer:
                if curScorer == "home":
                    lastHomeSeq += 1
                else:
                    lastAwaySeq += 1
            else:
                # check if goal has been hit
                if (
                    lastHomeSeq > 2
                    and lastScore["away"] > 2
                    and item["home"] - item["away"] >= 0
                ):
                    self.add_score(POINTS_COME_BACK)
                if (
                    lastAwaySeq > 2
                    and lastScore["home"] > 2
                    and item["away"] - item["home"] >= 0
                ):
                    self.add_score(POINTS_COME_BACK)

                lastHomeSeq, lastAwaySeq = 0, 0
                if curScorer == "home":
                    lastHomeSeq = 1
                else:
                    lastAwaySeq = 1

            # print(curScorer, lastAwaySeq, lastHomeSeq)

            lastHome, lastAway = item["home"], item["away"]
            lastScorer = curScorer
            lastScore = item

        if (
            lastHomeSeq > 2
            and lastScore["away"] > 2
            and lastScore["home"] - lastScore["away"] >= 0
        ):
            self.add_score(POINTS_COME_BACK)
        if (
            lastAwaySeq > 2
            and lastScore["home"] > 2
            and lastScore["away"] - lastScore["home"] >= 0
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
        allRegular3rdGoals = filter(
            lambda x: x["about"]["periodType"] == "REGULAR"
            and x["about"]["ordinalNum"] == "3rd"
            and x["result"]["eventTypeId"] == "GOAL"
            and x["result"]["emptyNet"],
            self.game["liveData"]["plays"]["allPlays"],
        )

        if len(list(allRegular3rdGoals)) > 0:
            self.add_score(POINTS_MISSED_CHANCE)

    def gatherNoticablePlayers(self) -> list:
        awayPlayers = list(
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

        homePlayers = list(
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
            for x in awayPlayers + homePlayers
        ]

    # hat-trick, 3 goals by one player
    # poker trick, 4 goals by one player
    # 5+ goals by one player
    def findTricks(self, noticablePlayers):
        hatTricks = len(list(filter(lambda x: x["goals"] == 3, noticablePlayers)))
        pokerTricks = len(list(filter(lambda x: x["goals"] == 4, noticablePlayers)))
        moreTricks = len(list(filter(lambda x: x["goals"] > 4, noticablePlayers)))
        if hatTricks > 0:
            self.add_score(POINTS_HAT_TRICK, hatTricks)
        if pokerTricks > 0:
            self.add_score(POINTS_POKER, pokerTricks)
        if moreTricks > 0:
            self.add_score(POINTS_MAD_SCORER)

    # Star shines / Star has points, 1+ goal Or 2+ assists, 3+ points by any star
    def findStarShines(self, noticablePlayers):
        starShinesCount = 0
        starHasPoints = 0
        for player in noticablePlayers:
            if player["id"] in STARS:
                starHasPoints += 1

                if (
                    player["goals"] > 0
                    or player["assists"] > 1
                    or (player["goals"] + player["assists"]) > 2
                ):
                    starShinesCount += 1
                    starHasPoints -= 1

        if starHasPoints > 0:
            self.add_score(POINTS_STAR_POINTS)

        if starShinesCount > 0:
            self.add_score(POINTS_STAR_SHINES)

    # Points master, no star players with 3+ points
    def findPointsMaster(self, noticablePlayers):
        playersWithBigPoints = 0
        for player in noticablePlayers:
            if player not in STARS and (player["goals"] + player["assists"]) > 2:
                playersWithBigPoints += 1

        if playersWithBigPoints > 0:
            self.add_score(POINTS_MASTER, playersWithBigPoints)

    def add_score(self, scoreType: str, scoreMultiplicator: int = 1):
        self.points.append(
            {"code": scoreType, "points": ALL_POINTS[scoreType] * scoreMultiplicator}
        )
