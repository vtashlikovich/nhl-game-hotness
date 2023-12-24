import pytest
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from lib import GameStats, POINTS_SO
from utils import load_game, get_found_point_types

# SO
game_id = 2021020167

@pytest.fixture
def game_stats():
    game_json = load_game(game_id)
    stats_json = load_game(game_id, '.boxscore')
    return GameStats(game_json, stats_json)

def test_find_SO(game_stats):
    game_stats.find_SO()
    assert POINTS_SO in get_found_point_types(game_stats)