#!/usr/bin/env python

import sys, getopt, json, logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timedelta
from lib.gameliststats import GameListStats

today = datetime.now()
cur_date = today.strftime("%Y-%m-%d")
cli_date = None
dump_file_path = None
dump_dir = None
live_results = True
days_back = 3

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
    opts, arg = getopt.getopt(sys.argv[1:], "b:d:f:l:s")
    for opt, arg_value in opts:
        if opt == "-d":
            cli_date = arg_value
        elif opt == "-f":
            dump_file_path = arg_value
        elif opt == "-l":
            dump_dir = arg_value
        elif opt == "-s":
            live_results = False
        elif opt == "-b":
            days_back = int(arg_value)
except getopt.GetoptError:
    print("usage: games.py [-d YYYY-MM-DD] [-b DAYS_BACK] [-f dump_file.json] [-l auto_file_location_dir] [-s]")
    logger.critical(f"wrong args: {sys.argv}")
    sys.exit(2)

if cli_date is not None:
    start_date = cli_date
else:
    earlier_n_days = today - timedelta(days=days_back)
    start_date = earlier_n_days.strftime("%Y-%m-%d")

if dump_dir is not None:
    dump_file_path = dump_dir + "/" + cur_date + ".json"

print("NHL games hotness points from " + start_date + " till today")
if dump_file_path is not None:
    print("Dumping json to " + dump_file_path)
    logger.info(f"going to dump to: {dump_file_path}")

game_analyzer = GameListStats(start_date, cur_date, logger=logger)
game_analyzer.think(log_live_result=live_results)

if dump_file_path is not None:
    try:
        output_file = open(dump_file_path, "w")
    except OSError:
        print("Could not open file for writing: " + dump_file_path)
        logger.critical("couldn't open dump file")
        sys.exit()

    with output_file:
        output_file.write(
            json.dumps(
                sorted(
                    game_analyzer.results, reverse=True, key=lambda x: int(x["date"].replace("-", ""))
                )
            )
        )
        print("Information is dumped to " + dump_file_path)
        logger.info("informarion is dumped")
