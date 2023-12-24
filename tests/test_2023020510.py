import pytest
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from lib import GameStats, POINTS_COME_BACK, POINTS_OT, POINTS_SO
from utils import load_game, get_found_point_types

# comeback + OT + SO
game_id = 2023020510

@pytest.fixture
def game_stats():
    game_json = load_game(game_id)
    stats_json = load_game(game_id, '.boxscore')
    return GameStats(game_json, stats_json)

def test_comeback(game_stats):
    game_stats.find_come_back()
    assert POINTS_COME_BACK in get_found_point_types(game_stats), 'Come back not found'

def test_ot(game_stats):
    game_stats.find_OT()
    assert POINTS_OT in get_found_point_types(game_stats), 'Overtime not found'

def test_so(game_stats):
    game_stats.find_SO()
    assert POINTS_SO in get_found_point_types(game_stats), 'Shootout not found'
