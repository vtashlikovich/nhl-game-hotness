import logging
import logging.handlers
from logging.handlers import TimedRotatingFileHandler
from flask import Flask, json, request, session
from flask_compress import Compress
from datetime import datetime, timedelta
from lib.gameliststats import GameListStats
from waitress import serve

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handler 
LOG_FILE = './logs/access.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1048576, backupCount=5)
handler.setLevel(logging.INFO)

# Create handler/formatter for the cron job
LOGGING_MSG_FORMAT  = '%(asctime)s - %(levelname)s - %(message)s'
LOGGING_DATE_FORMAT = '%m-%d %H:%M:%S'
LOG_LOCATION = "./logs/app.log"
formatter = logging.Formatter(LOGGING_MSG_FORMAT, LOGGING_DATE_FORMAT)
cronhandler = TimedRotatingFileHandler(LOG_LOCATION, 'midnight', 1)
cronhandler.namer = lambda name: name.replace(".log", "") + ".log"
cronhandler.setFormatter(formatter)
cronhandler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add Formatter to Handler
handler.setFormatter(formatter)

# add Handler to Logger
logger.addHandler(handler)

application = Flask(__name__, static_url_path="", static_folder="web")
application.secret_key = b"er5rhMNjjEF6kd4F_541"
compress = Compress()
compress.init_app(application)

# server routing
@application.route("/")
def rootRouteProcessor():
    logger.info(f"{request.remote_addr}, /, {request.user_agent}")
    return application.send_static_file("index.html")

@application.route("/updatenhlgamesLU6QxuMVyzyrHNqV", methods=["POST"])
def updategamesProcessor():
    global application

    cronlogger = logging.getLogger("filelogger")
    cronlogger.setLevel(logging.INFO)
    cronlogger.addHandler(cronhandler)

    cronlogger.info("")

    logger.info(f"Received scheduled task, {request.remote_addr}, {request.user_agent}")

    today = datetime.now()
    curDate = today.strftime("%Y-%m-%d")
    earlier3days = today - timedelta(days=3)
    startDate = earlier3days.strftime("%Y-%m-%d")
    dumpFilePath = "web/log/" + curDate + ".json"

    cronlogger.info(f"going to dump to: {dumpFilePath}")

    gameAnalyzer = GameListStats(startDate, curDate, logger=cronlogger)
    gameAnalyzer.think()

    if dumpFilePath is not None:
        try:
            outputFile = open(dumpFilePath, "w")
        except OSError:
            print("Could not open file for writing: " + dumpFilePath)
            cronlogger.critical("couldn't open dump file")

        with outputFile:
            outputFile.write(
                json.dumps(
                    sorted(
                        gameAnalyzer.results, reverse=True, key=lambda x: int(x["date"].replace("-", ""))
                    )
                )
            )
            print("Information is dumped to " + dumpFilePath)
            cronlogger.info("informarion is dumped")

    return json.dumps({"success": True}), 201

# server start
if __name__ == "__main__":
    # api.debug = True
    # application.run()
    serve(application, host="0.0.0.0", port=5000)