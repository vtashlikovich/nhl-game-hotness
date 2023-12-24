import pytest
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from lib import GameStats, POINTS_OT, POINTS_TIGHT_FIGHT
from utils import load_game, get_found_point_types

# Columbus - WSH, OT win
game_id = 2023020499

@pytest.fixture
def game_stats():
    game_json = load_game(game_id)
    stats_json = load_game(game_id, '.boxscore')
    return GameStats(game_json, stats_json)

def test_find_OT(game_stats):
    game_stats.find_OT()
    assert POINTS_OT in get_found_point_types(game_stats)

def test_find_tight_fight(game_stats):
    game_stats.find_tight_fight()
    assert POINTS_TIGHT_FIGHT in get_found_point_types(game_stats)