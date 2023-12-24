import pytest
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from lib import GameStats, POINTS_OT, POINTS_HIGH_TENSION
from utils import load_game, get_found_point_types

# OT, 4:5, star scores
game_id = 2021020152

@pytest.fixture
def game_stats():
    game_json = load_game(game_id)
    stats_json = load_game(game_id, '.boxscore')
    return GameStats(game_json, stats_json)

def test_find_ot(game_stats):
    game_stats.find_OT()
    assert POINTS_OT in get_found_point_types(game_stats)

def test_find_high_tension(game_stats):
    game_stats.find_high_tension()
    assert POINTS_HIGH_TENSION in get_found_point_types(game_stats)