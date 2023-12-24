import pytest
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from lib import GameStats, POINTS_COME_BACK, POINTS_LATE_TIGHT_WIN1_20
from utils import load_game, get_found_point_types

# comeback + late tight win1_20
game_id = 2023020515

@pytest.fixture
def game_stats():
    game_json = load_game(game_id)
    stats_json = load_game(game_id, '.boxscore')
    return GameStats(game_json, stats_json)

def test_comeback(game_stats):
    game_stats.find_come_back()
    assert POINTS_COME_BACK in get_found_point_types(game_stats), 'Come back not found'

def test_late_tight_win1(game_stats):
    game_stats.find_tight_win1()
    assert POINTS_LATE_TIGHT_WIN1_20 in get_found_point_types(game_stats), 'Late tight win 1_20 not found'
