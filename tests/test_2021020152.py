import pytest
import json
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from lib import GameStats, POINTS_OT, POINTS_HIGH_TENSION

# OT, 4:5, star scores
game_id = 2021020152

def load_game(game_id, file_postfix=''):
    result = None
    with open('samples/' + str(game_id) + file_postfix + '.json') as game_file:
        result = json.loads(game_file.read())
    return result


@pytest.fixture
def game_stats():
    game_json = load_game(game_id)
    stats_json = load_game(game_id, '.boxscore')
    return GameStats(game_json, stats_json)

def test_find_ot(game_stats):
    game_stats.find_OT()
    point_types = [k['code'] for k in game_stats.getPoints()]
    assert POINTS_OT in point_types

def test_find_high_tension(game_stats):
    game_stats.find_high_tension()
    point_types = [k['code'] for k in game_stats.getPoints()]
    assert POINTS_HIGH_TENSION in point_types