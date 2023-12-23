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

PERIOD_END = 521
GAME_END = 524


class GameStats:
    def __init__(self, game_json: dict, stats_json: dict):
        self.game = game_json
        self.stats = stats_json
        self.points = []
        self.points_sum = 0

    def think(self):
        if 'plays' in self.game.keys():
            # OT
            self.find_OT()

            # S/O
            self.find_SO()

            # Long S/O session
            self.find_long_SO()

            # Tight fight, 28+ shots by both teams in regular
            self.find_tight_fight()

            # The wall, 35+ saves by any goalkeeper in regular
            self.find_the_wall()

            # High tension: OT, when regular ends with 4:4+
            self.find_high_tension()

            # Last chance, OT set up on the last minute/20/5 seconds of regular
            self.find_last_chance()

            # Late winner, Goal on the last 15 seconds of OT
            self.find_late_OT_winner()

            # Tight win, both scores 3+, games ends regular with 1 puck difference
            # Late tight win, Tight win and the winning goal with in the last minute of 3rd
            self.find_tight_win()

            # Come back, 3+ straight goals, up to even score or advantage
            self.find_come_back()

            # Equal play (1:1, 2:2, 3:3, ..) up to 2/3 times per game
            self.find_equal_game()

            # Missed chance, in 3rd period a game no goalkeeper, opponent scores in empty net
            self.find_missed_chance()

            noticable_players = self.gather_noticable_players()

            # hat-trick, 3 goals by one player
            # poker, 4 goals by one player
            # 5+ goals by one player, madness
            self.find_tricks(noticable_players)

            # Star shines, star player with 1+ goal or 2+ assists or 3+ points
            # Star scores, star player has at least 1 point
            self.find_star_shines(noticable_players)

            # Points master, no star players with 3+ points
            self.find_points_master(noticable_players)

            # TODO: goal while having own empty net
            # 2021020319

            # TODO: too many goals - 4 points for each 5 goals by 1 team
            # TODO: too many goals - 3 points if team scored >= 7

            # TODO: 1 point for each goal ?

            # TODO: points for lots of penalties

            # TODO: points for no goals while 3 on 5

            # TODO: determine a fight in the game

            # TODO: team with league bottom beats high league team

            # TODO: points for penulty shot ?

            # TODO: empty net - goal post

            # TODO: points for lots of post/bar shots

            # TODO: goal on the first seconds

            # TODO: shorthanded goals (in minority)

            # TODO: Start goalie shines, star golie with 30+ saves
            # TODO: Gordie Howe hat-trick, 1 goal, 1 assist, 1 fight

            # TODO: if few points - add points if more than 3 pucks are scored in the game
            # homeGoals, awayGoals = self.getRegularItems("goals")

            self.points_sum = sum([x['points'] for x in self.getPoints()])

    def getPoints(self) -> list:
        return self.points

    def isHot(self) -> bool:
        return self.points_sum >= LEVEL_HOT

    def isWow(self) -> bool:
        return self.points_sum >= LEVEL_WOW

    def game_finished(self):
        return self.game['plays'][-1]['typeCode'] == GAME_END

    def find_last_period_type(self):
        return self.game['plays'][-1]['periodDescriptor']['periodType']

    def game_ended_in_3rd(self):
        event_info = self.game['plays'][-1]['periodDescriptor']
        return event_info['periodType'] == 'REG' and event_info['number'] == 3

    def find_OT(self):
        if (self.game_finished() and
                self.find_last_period_type() in ['OT', 'SO']):
            self.add_score(POINTS_OT)

    def find_SO(self):
        if (self.game_finished() and
                self.find_last_period_type() == 'SO'):
            self.add_score(POINTS_SO)

    def find_long_SO(self):
        shootouts_num = len([game for game in self.game['plays']
                             if game['periodDescriptor']['periodType'] == 'SO' and
                             not game['typeDescKey'] in ['shootout-complete', 'period-start']])
        if (self.game_finished() and
                self.find_last_period_type == 'SO' and
                shootouts_num > 3):
            if (shootouts_num > 7):
                self.add_score(POINTS_LONG_SO_EXTRA)
            else:
                self.add_score(POINTS_LONG_SO)

    def find_all_shots(self):
        return [(event['details']['awaySOG'], event['details']['homeSOG'])
                for event in self.game['plays'] if event['typeDescKey'] == 'shot-on-goal']

    def find_all_goals(self):
        return [(event['details']['awayScore'], event['details']['homeScore'])
                for event in self.game['plays'] if event['typeDescKey'] == 'goal']

    def find_regular_goals(self):
        return [(event['details']['awayScore'], event['details']['homeScore'])
                for event in self.game['plays'] if event['typeDescKey'] == 'goal' and
                event['periodDescriptor']['periodType'] == 'REG']

    # Tight fight, 28+ shots by both teams in regular
    def find_tight_fight(self):
        shots = self.find_all_shots()

        away_shots, home_shots = shots[-1]

        if home_shots > 27 and away_shots > 27:
            self.add_score(POINTS_TIGHT_FIGHT)

    # The wall, 35+ saves by any goalkeeper in regular
    def find_the_wall(self):
        shots = self.find_all_shots()
        goals = self.find_all_goals()

        away_shots, home_shots = shots[-1]
        away_goals, home_goals = goals[-1]

        away_goalie_saves = home_shots - home_goals
        home_goalie_saves = away_shots - away_goals

        if away_goalie_saves > 34 or home_goalie_saves > 34:
            self.add_score(POINTS_WALL)

    def find_high_tension(self):
        away_regular_goals, home_regular_goals = self.find_regular_goals()[-1]

        if (self.game_finished() and
                self.find_last_period_type() in ['OT', 'SO'] and
                home_regular_goals > 3 and away_regular_goals > 3):
            self.add_score(POINTS_HIGH_TENSION)

    # get time left of the last goal before the specified period end
    def get_last_goal_left_time(self, period_name) -> int:
        time = -1

        # collect list of time remaining
        all_goal_left_times = [event['timeRemaining'] for event in self.game['plays']
                               if event['periodDescriptor']['periodType'] == period_name and
                               event['typeDescKey'] == 'goal']

        # find tha latest goal - calc time remaining to the end of period
        if len(all_goal_left_times) > 0:
            lat_goal_time = all_goal_left_times[-1].split(":")
            if len(lat_goal_time) == 2:
                time = int(lat_goal_time[0]) * 60 + int(lat_goal_time[1])

        return time

    # Last chance, OT set up on the last minute/20/5 seconds of regular
    def find_last_chance(self):
        last_goal_left_time = self.get_last_goal_left_time("REG")

        if (self.game_finished() and
                self.find_last_period_type() in ['OT', 'SO'] and
                last_goal_left_time != -1):
            if last_goal_left_time < 6:
                self.add_score(POINTS_LAST_CHANCE5)
            elif last_goal_left_time < 21:
                self.add_score(POINTS_LAST_CHANCE20)
            elif last_goal_left_time < 61:
                self.add_score(POINTS_LAST_CHANCE)

    # Late winner, Goal on the last 15 seconds of OT
    def find_late_OT_winner(self):
        last_goal_left_time = self.get_last_goal_left_time('OT')
        if (self.find_last_period_type() == 'OT' and
                last_goal_left_time != -1 and
                last_goal_left_time < 16):
            self.add_score(POINTS_LATE_WINNER)

    # Tight win, both scores 3+, games ends regular with 1 puck difference
    # bonus for the last minute goal
    def find_tight_win(self):
        goals = self.find_all_goals()
        away_goals, home_goals = goals[-1]

        if (self.game_ended_in_3rd() and
                home_goals > 2 and away_goals > 2 and abs(home_goals - away_goals) == 1):
            self.add_score(POINTS_TIGHT_WIN)

            # get the last goal time left
            last_goal_left_time = self.get_last_goal_left_time('REG')

            if (goals[-2][0] == goals[-2][1] and last_goal_left_time != -1):
                if last_goal_left_time < 21:
                    self.add_score(POINTS_LATE_TIGHT_WIN20)
                elif last_goal_left_time < 61:
                    self.add_score(POINTS_LATE_TIGHT_WIN)

    # Come back, 3+ straight goals, up to equal score or advantage (opponent scores 3+)
    def find_come_back(self):
        all_regular_goals = self.find_regular_goals()

        last_home = 0
        last_scorer = 'none'
        last_home_seq, last_away_seq = 0, 0
        last_score = (0, 0)

        # item = (away, home)
        for item in all_regular_goals:
            # print(item)
            cur_scorer = 'none'
            if item[1] > last_home:
                cur_scorer = 'home'
            else:
                cur_scorer = 'away'

            if cur_scorer == last_scorer:
                if cur_scorer == 'home':
                    last_home_seq += 1
                else:
                    last_away_seq += 1
            else:
                # check if goal has been hit
                if (last_home_seq > 2 and last_score[0] > 2 and
                        item[1] - item[0] >= 0):
                    self.add_score(POINTS_COME_BACK)
                if (last_away_seq > 2 and last_score[1] > 2 and
                        item[0] - item[1] >= 0):
                    self.add_score(POINTS_COME_BACK)

                last_home_seq, last_away_seq = 0, 0
                if cur_scorer == 'home':
                    last_home_seq = 1
                else:
                    last_away_seq = 1

            # print(curScorer, lastAwaySeq, lastHomeSeq)

            last_home = item[1]
            last_scorer = cur_scorer
            last_score = item

        if (last_home_seq > 2 and last_score[0] > 2 and last_score[1] - last_score[0] >= 0):
            self.add_score(POINTS_COME_BACK)
        if (last_away_seq > 2 and last_score[1] > 2 and last_score[0] - last_score[1] >= 0):
            self.add_score(POINTS_COME_BACK)

    # Equal play up to 3:3, e.g.: 1:0, 1:1, 2:1, 2:2, 3:2, 3:3, ...
    def find_equal_game(self):
        all_regular_goals = self.find_regular_goals()

        equal_game_counter = 0
        for item in all_regular_goals:
            if item[1] == item[0]:
                equal_game_counter += 1

        if equal_game_counter == 2:
            self.add_score(POINTS_EQUAL_GAME)
        elif equal_game_counter > 2:
            self.add_score(POINTS_EQUAL_GAME3)

    # Missed chance, in 3rd period a game no goalkeeper, opponent scores in empty net
    def find_missed_chance(self):
        if self.game_ended_in_3rd():
            all_regular_3rd_goals = [event['details'] for event in self.game['plays']
                                     if event['typeDescKey'] == 'goal' and
                                     event['periodDescriptor']['periodType'] == 'REG']

            last_goal_event = all_regular_3rd_goals[-1]

            if 'goalieInNetId' not in last_goal_event:
                self.add_score(POINTS_MISSED_CHANCE)

    def gather_noticable_players(self) -> list:
        if self.stats:
            away_players_forwards = [event for event in
                                     self.stats['boxscore']['playerByGameStats']['awayTeam']['forwards']]
            away_players_defense = [event for event in
                                    self.stats['boxscore']['playerByGameStats']['awayTeam']['defense']]

            home_players_forwards = [event for event in
                                     self.stats['boxscore']['playerByGameStats']['homeTeam']['forwards']]
            home_players_defense = [event for event in
                                    self.stats['boxscore']['playerByGameStats']['homeTeam']['defense']]

            return [
                {
                    'id': x['playerId'],
                    'goals': x['goals'],
                    'assists': x['assists']
                }
                for x in away_players_forwards + away_players_defense + home_players_forwards +
                home_players_defense
            ]

    # hat-trick, 3 goals by one player
    # poker trick, 4 goals by one player
    # 5+ goals by one player
    def find_tricks(self, noticable_players):
        hat_tricks = len(list(filter(lambda x: x['goals'] == 3, noticable_players)))
        poker_tricks = len(list(filter(lambda x: x['goals'] == 4, noticable_players)))
        more_tricks = len(list(filter(lambda x: x['goals'] > 4, noticable_players)))
        if hat_tricks > 0:
            self.add_score(POINTS_HAT_TRICK, hat_tricks)
        if poker_tricks > 0:
            self.add_score(POINTS_POKER, poker_tricks)
        if more_tricks > 0:
            self.add_score(POINTS_MAD_SCORER)

    # Star shines / Star has points, 1+ goal Or 2+ assists, 3+ points by any star
    def find_star_shines(self, noticable_players):
        star_shines_count = 0
        star_has_points = 0

        for player in noticable_players:
            if player['id'] in STARS:
                star_has_points += 1

                if (player['goals'] > 0 or player['assists'] > 1 or (player['goals'] + player['assists']) > 2):
                    star_shines_count += 1
                    star_has_points -= 1

        if star_has_points > 0:
            self.add_score(POINTS_STAR_POINTS)

        if star_shines_count > 0:
            self.add_score(POINTS_STAR_SHINES)

    # Points master, no star players with 3+ points
    def find_points_master(self, noticable_players):
        players_with_big_points = 0
        for player in noticable_players:
            if player not in STARS and (player['goals'] + player['assists']) > 2:
                players_with_big_points += 1

        if players_with_big_points > 0:
            self.add_score(POINTS_MASTER, players_with_big_points)

    def add_score(self, score_type: str, score_multiplicator: int = 1):
        self.points.append(
            {"code": score_type, "points": ALL_POINTS[score_type] * score_multiplicator}
        )
