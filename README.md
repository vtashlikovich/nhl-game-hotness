# NHL game hotness meter

## About

If you love hockey, NHL, if you track your favorite teams' progress but eagure to see any really __hot__ game replay... But you are stuck to determine which one is good? This tool will help.

This python CLI utility analyzes NHL game data and calculates hottness points. If you see _HOT_ next to the game - that's worth seeing. If you get _WOW!_ next to the game - you must watch this.

![NHL game hottness log](i/log_screen.png)

## How scoring is done

Scoring is calculated on the base of data provided by public NHL API (https://statsapi.web.nhl.com).

_gamestats.py_ lib uses the following metrics to get points for each game.

__Overtime__. If teams got to OT.

__Shootout__. If teams reached to SO.

__Long shootout__. If rounds are more than 3.

__Extra long shootout__. If rounds are more than 7.

__Tight fight__. 28+ shots made by both teams.

__The wall__. 35+ saves by any goalkeepr in regular.

__High tension__. When regular ends with score 4:4+.

__Last chance__. When OT set up in the last minute.

__Last chance 20__. When OT set up in the 20 seconds.

__Last chance 5__. When OT set up in the 5 seconds.

__Late winner__. Winning goal in the last 15 seconds of OT.

__Tight win__. Both teams score 3+, regular ends with 1 puck difference only.

__Come back__. One team scores 3+ straight that leads to even score or advantage.

__Equal game__. Both game reach equal score at least 2 times per game.

__Equal game 3__. Both game reach equal score at least 3 times per game.

__Missed chance__. 3rd period, no goalkeeper but opponent scores.

__Hat trick__. 1 player gets a hatty.

__Poker__. 1 player gets a poker.

__Mad scorer__. 1 player scores 5+.

__Star points__. Star player has 1 point in the game.

__Star shines__. Star player has 2+ goals, 2+ assits or 3+ points.

__Points master__. Player (not a star) gets 3+ points per game.

## How to run

```bash
# get hockey games points for the last 3 days
$ python games.py

# get hockey games points for the period from DATE to the current date
# DATE is of YYYY-MM-DD format
$ python games.py DATE

# get hottness points for a single game
$ python onegame.py GAME_ID
```

Or make index.py and onegame.py files runnable (Unix/Linux/MacOs) and run as a bash script.

```bash
$ chmod +x index.py

$ ./games.py
```

## Enjoy!