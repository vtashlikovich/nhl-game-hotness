import requests
from functools import reduce
from operator import add

API_URL = "https://statsapi.web.nhl.com/api/v1"

response = requests.get(API_URL + "/people/8471214/stats?stats=gameLog", params={"Content-Type": "application/json"})
data = response.json()

# print(data)

filteredGames = filter(lambda item: item["stat"]["points"] > 2, data["stats"][0]["splits"])
for game in filteredGames:
    ratio = 'N/A'
    
    if game['stat']['goals'] > 0:
        ratio = "{0:.2f}".format(game['stat']['shots'] / game['stat']['goals'])

    print(f"Game: {game['date']}, points={game['stat']['points']}, goals={game['stat']['goals']}, shots={game['stat']['shots']}, ratio={ratio}")

print("---")

filteredGames = list(filter(lambda item: item["stat"]["games"] == 1, data["stats"][0]["splits"]))
pointsGenerator = map(lambda x: x["stat"]["points"], filteredGames)
goalsGenerator = map(lambda x: x["stat"]["goals"], filteredGames)
totalGamesCount = len(filteredGames)
totalPointsNum = reduce(add, pointsGenerator)
totalGoalsNum = reduce(add, goalsGenerator)
print("Total games:", totalGamesCount)
print("Total goals:", totalGoalsNum)
print("Points ratio:", "{0:.2f}".format(totalPointsNum/totalGamesCount))
print("Goals ratio:", "{0:.2f}".format(totalGoalsNum/totalGamesCount))