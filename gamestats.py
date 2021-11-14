from functools import reduce
import itertools

STARS = [
    8477934,  # Draisaitl
    8478402,  # McDavid
    8471214,  # Ovechkin
    8473419,  # Marchand
    8475744,  # Kuznetsov
    8471685,  # Kopitar
    8474600,  # Josi
    8475166,  # Tavares
    8474564,  # Stamkos
    8478550,  # Panarin
    8475765,  # Tarasenko
    8476459,  # Zibanejad
    8479318,  # Matthews
    8470794,  # Pavelski
    8474141,  # Patrick Kane
    8476453,  # Kucherov
    8471675,  # Crosby
]

POINTS_OT = 3
POINTS_SO = 2
POINTS_LONG_SO = 1
POINTS_LONG_SO_EXTRA = 2
POINTS_TIGHT_FIGHT = 2
POINTS_WALL = 2
POINTS_HIGH_TENSION = 2
POINTS_LAST_CHANCE = 1
POINTS_LAST_CHANCE20 = 2
POINTS_LAST_CHANCE5 = 3
POINTS_LATE_WINNER = 2
POINTS_TIGHT_WIN = 2
POINTS_COME_BACK = 3
POINTS_EQUAL_GAME = 2
POINTS_EQUAL_GAME3 = 3
POINTS_MISSED_CHANCE = 2
POINTS_HAT_TRICK = 2
POINTS_POKER = 4
POINTS_MAD_SCORER = 10
POINTS_STAR_SHINES = 2


class GameStats:
    def __init__(self, json: dict):
        self.game = json
        self.points = []

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
            self.findTightWin()

            # Come back, 3+ straight goals, up to even score or advantage
            self.findComeBack()

            # Equal play (1:1, 2:2, 3:3, ..) up to 2/3 times per game
            self.findEqualGame()

            # Missed chance, in 3rd period a game no goalkeeper, opponent scores in empty net
            self.findMissedChance()

            noticablePlayers = self.gatherPlayerStats()

            # hat-trick, 3 goals by one player
            # poker trick, 4 goals by one player
            # 5+ goals by one player
            self.findTricks(noticablePlayers)

            # Star shines, 1+ goal Or 2+ assists, 3+ points
            self.findStarShines(noticablePlayers)

            # Gordie Howe hat-trick, 1 goal, 1 assist, 1 fight

    def getPoints(self) -> list:
        return self.points

    def findOT(self):
        if (
            self.game["liveData"]["linescore"]["currentPeriodOrdinal"] in ["OT", "SO"]
            and self.game["liveData"]["linescore"]["currentPeriodTimeRemaining"]
            == "Final"
        ):
            self.points.append({"name": "OT", "points": POINTS_OT})

    def findSO(self):
        if (
            self.game["liveData"]["linescore"]["currentPeriodOrdinal"] == "SO"
            and self.game["liveData"]["linescore"]["currentPeriodTimeRemaining"]
            == "Final"
        ):
            self.points.append({"name": "SO", "points": POINTS_SO})

    def findLongSO(self):
        if (
            self.game["liveData"]["linescore"]["currentPeriodOrdinal"] == "SO"
            and self.game["liveData"]["linescore"]["currentPeriodTimeRemaining"]
            == "Final"
            and self.game["liveData"]["linescore"]["shootoutInfo"]["home"]["attempts"]
            > 3
        ):
            self.points.append({"name": "Long SO", "points": POINTS_LONG_SO})

            if (
                self.game["liveData"]["linescore"]["shootoutInfo"]["home"]["attempts"]
                > 7
            ):
                self.points.append(
                    {"name": "Long SO extra", "points": POINTS_LONG_SO_EXTRA}
                )

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
            self.points.append({"name": "Tight fight", "points": POINTS_TIGHT_FIGHT})

    # The wall, 35+ saves by any goalkeeper in regular
    def findTheWall(self):
        homeShots, awayShots = self.getRegularItems("shotsOnGoal")
        homeGoals, awayGoals = self.getRegularItems("goals")

        awayGoalieSaves = homeShots - homeGoals
        homeGoalieSaves = awayShots - awayGoals

        if awayGoalieSaves > 34 or homeGoalieSaves > 34:
            self.points.append({"name": "The wall", "points": POINTS_WALL})

    def findHighTension(self):
        homeRegularGoals, awayRegularGoals = self.getRegularItems("goals")

        if (
            self.game["liveData"]["linescore"]["currentPeriodOrdinal"] in ["OT", "SO"]
            and homeRegularGoals > 3
            and awayRegularGoals > 3
        ):
            self.points.append({"name": "High tension", "points": POINTS_HIGH_TENSION})

    # get time left of the last goal before the specified period end
    def getLastGoalLeftTime(self, periodName) -> int:
        time = -1

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
            if lastGoalLeftTime < 61:
                self.points.append(
                    {"name": "Last chance", "points": POINTS_LAST_CHANCE}
                )
            elif lastGoalLeftTime < 21:
                self.points.append(
                    {"name": "Last chance 20", "points": POINTS_LAST_CHANCE20}
                )
            elif lastGoalLeftTime < 6:
                self.points.append(
                    {"name": "Last chance 5", "points": POINTS_LAST_CHANCE5}
                )

    # Late winner, Goal on the last 15 seconds of OT
    def findLateOTWinner(self):
        lastGoalLeftTime = self.getLastGoalLeftTime("OVERTIME")
        if (
            self.game["liveData"]["linescore"]["currentPeriodOrdinal"] == "OT"
            and lastGoalLeftTime != -1
            and lastGoalLeftTime < 16
        ):
            self.points.append({"name": "Last chance", "points": POINTS_LATE_WINNER})

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
            self.points.append({"name": "Tight win", "points": POINTS_TIGHT_WIN})

    def getRegularGoals(self) -> list:
        allRegularGoals = filter(
            lambda x: x["about"]["periodType"] == "REGULAR"
            and x["result"]["eventTypeId"] == "GOAL",
            self.game["liveData"]["plays"]["allPlays"],
        )

        return [x["about"]["goals"] for x in allRegularGoals]

    # Come back, 3+ straight goals, up to equal score or advantage (opponent scores 3+)
    def findComeBack(self):
        allRegularGoals = self.getRegularGoals()

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
                    self.points.append(
                        {"name": "Come back", "points": POINTS_COME_BACK}
                    )
                if (
                    lastAwaySeq > 2
                    and lastScore["home"] > 2
                    and item["away"] - item["home"] >= 0
                ):
                    self.points.append(
                        {"name": "Come back", "points": POINTS_COME_BACK}
                    )

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
            self.points.append({"name": "Come back", "points": POINTS_COME_BACK})
        if (
            lastAwaySeq > 2
            and lastScore["home"] > 2
            and lastScore["away"] - lastScore["home"] >= 0
        ):
            self.points.append({"name": "Come back", "points": POINTS_COME_BACK})

    # Equal play up to 3:3, e.g.: 1:0, 1:1, 2:1, 2:2, 3:2, 3:3, ...
    def findEqualGame(self):
        allRegularGoals = self.getRegularGoals()

        equalGameCounter = 0
        for item in allRegularGoals:
            if item["home"] == item["away"]:
                equalGameCounter += 1

        if equalGameCounter == 2:
            self.points.append({"name": "Equal game", "points": POINTS_EQUAL_GAME})
        elif equalGameCounter > 2:
            self.points.append({"name": "Equal game 3", "points": POINTS_EQUAL_GAME3})

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
            self.points.append(
                {"name": "Missed chance", "points": POINTS_MISSED_CHANCE}
            )

    def gatherPlayerStats(self) -> list:
        awayPlayers = list(
            filter(
                lambda x: x["position"]["code"] != "G"
                and "skaterStats" in x["stats"]
                and (
                    x["stats"]["skaterStats"]["goals"] > 0
                    or x["stats"]["skaterStats"]["assists"] > 1
                    or x["stats"]["skaterStats"]["assists"]
                    + x["stats"]["skaterStats"]["goals"]
                    > 2
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
                    or x["stats"]["skaterStats"]["assists"] > 1
                    or x["stats"]["skaterStats"]["assists"]
                    + x["stats"]["skaterStats"]["goals"]
                    > 2
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
            self.points.append(
                {"name": "Hat trick(s)", "points": POINTS_HAT_TRICK * hatTricks}
            )
        if pokerTricks > 0:
            self.points.append(
                {"name": "Poker trick(s)", "points": POINTS_POKER * pokerTricks}
            )
        if moreTricks > 0:
            self.points.append({"name": "Mad scorer", "points": POINTS_MAD_SCORER})

    # Star shines, 1+ goal Or 2+ assists, 3+ points
    def findStarShines(self, noticablePlayers):
        for player in noticablePlayers:
            if player in STARS:
                self.points.append(
                    {"name": "Star shines", "points": POINTS_STAR_SHINES}
                )
