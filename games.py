#!/usr/bin/env python

import sys
from datetime import datetime, timedelta
from lib.gameliststats import GameListStats

today = datetime.now()
curDate = today.strftime("%Y-%m-%d")

if len(sys.argv) > 1:
    startDate = sys.argv[1]
else:
    earlier3days = today - timedelta(days=3)
    startDate = earlier3days.strftime("%Y-%m-%d")

print("NHL games hotness points from " + startDate + " till today")

gameAnalyzer = GameListStats(startDate, curDate)
gameAnalyzer.think(logLiveResult = True)