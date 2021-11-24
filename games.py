#!/usr/bin/env python

import sys, getopt, json
from datetime import datetime, timedelta
from lib.gameliststats import GameListStats

today = datetime.now()
curDate = today.strftime("%Y-%m-%d")
cliDate = None
dumpFilePath = None
dumpDirectory = None
liveResults = True

try:
    opts, arg = getopt.getopt(sys.argv[1:], "d:f:l:s")
    for opt, arg_value in opts:
        if opt == "-d":
            cliDate = arg_value
        elif opt == "-f":
            dumpFilePath = arg_value
        elif opt == "-l":
            dumpDirectory = arg_value
        elif opt == "-s":
            liveResults = False
except getopt.GetoptError:
    print("usage: games.py [-d YYYY-MM-DD] [-f dump_file.json] [-l auto_file_location_dir] [-s]")
    sys.exit(2)

if cliDate is not None:
    startDate = cliDate
else:
    earlier3days = today - timedelta(days=3)
    startDate = earlier3days.strftime("%Y-%m-%d")

if dumpDirectory is not None:
    dumpFilePath = dumpDirectory + "/" + curDate + ".json"

print("NHL games hotness points from " + startDate + " till today")
if dumpFilePath is not None:
    print("Dumping json to " + dumpFilePath)

gameAnalyzer = GameListStats(startDate, curDate)
gameAnalyzer.think(logLiveResult=liveResults)

if dumpFilePath is not None:
    try:
        outputFile = open(dumpFilePath, "w")
    except OSError:
        print("Could not open file for writing: " + dumpFilePath)
        sys.exit()

    with outputFile:
        outputFile.write(
            json.dumps(
                sorted(
                    gameAnalyzer.results, reverse=True, key=lambda x: int(x["date"].replace("-", ""))
                )
            )
        )
        print("Information is dumped to " + dumpFilePath)
