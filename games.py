#!/usr/bin/env python

import sys, getopt, json, logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timedelta
from lib.gameliststats import GameListStats

today = datetime.now()
curDate = today.strftime("%Y-%m-%d")
cliDate = None
dumpFilePath = None
dumpDirectory = None
liveResults = True

LOGGING_MSG_FORMAT  = '%(asctime)s - %(levelname)s - %(message)s'
LOGGING_DATE_FORMAT = '%m-%d %H:%M:%S'
LOG_LOCATION = "./logs/app.log"

formatter = logging.Formatter(LOGGING_MSG_FORMAT, LOGGING_DATE_FORMAT)
handler = TimedRotatingFileHandler(LOG_LOCATION, 'midnight', 1)
handler.namer = lambda name: name.replace(".log", "") + ".log"
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

logger.info("")

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
    logger.critical(f"wrong args: {sys.argv}")
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
    logger.info(f"going to dump to: {dumpFilePath}")

gameAnalyzer = GameListStats(startDate, curDate, logger=logger)
gameAnalyzer.think(logLiveResult=liveResults)

if dumpFilePath is not None:
    try:
        outputFile = open(dumpFilePath, "w")
    except OSError:
        print("Could not open file for writing: " + dumpFilePath)
        logger.critical("couldn't open dump file")
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
        logger.info("informarion is dumped")
