#!/usr/bin/env python

import sys
import json
from lib.gamestats import GameStats
import traceback

game_path = ''
stats_path = ''

if len(sys.argv) > 2:
    game_path = sys.argv[1]
    stats_path = sys.argv[2]
else:
    print('files paths are needed')
    exit(1)

print(f'Check game {game_path} hotness')

try:
    with open(game_path) as game_file, open(stats_path) as stats_file:
        game_contents = game_file.read()
        stats_contents = stats_file.read()

        if game_contents is not None and stats_contents is not None:
            analyzer = GameStats(json.loads(game_contents), json.loads(stats_contents))
            analyzer.think()

            gamePoints = sum([x['points'] for x in analyzer.getPoints()])

            print(str(gamePoints))

            print(analyzer.getPoints())

except Exception as exc:
    traceback_info = sys.exc_info()
    print('Exception occured', type(exc).__name__, traceback_info)
    traceback.print_tb(exc.__traceback__)
