import pytest
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from lib import GameStats, POINTS_WALL, POINTS_TIGHT_WIN
from utils import load_game, get_found_point_types

# the wall, tight win2
game_id = 2021020180

@pytest.fixture
def game_stats():
    game_json = load_game(game_id)
    stats_json = load_game(game_id, '.boxscore')
    return GameStats(game_json, stats_json)

def test_find_wall(game_stats):
    game_stats.find_the_wall()
    assert POINTS_WALL in get_found_point_types(game_stats)

def test_find_tight_win2(game_stats):
    game_stats.find_tight_win2()
    assert POINTS_TIGHT_WIN in get_found_point_types(game_stats)