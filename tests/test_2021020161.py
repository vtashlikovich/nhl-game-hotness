import pytest
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from lib import GameStats, POINTS_OT, POINTS_LAST_CHANCE
from utils import load_game, get_found_point_types

# OT, regular equal score 24 sec before game end
game_id = 2021020161

@pytest.fixture
def game_stats():
    game_json = load_game(game_id)
    stats_json = load_game(game_id, '.boxscore')
    return GameStats(game_json, stats_json)

def test_ot(game_stats):
    game_stats.find_OT()
    assert POINTS_OT in get_found_point_types(game_stats)

def test_last_chance(game_stats):
    game_stats.find_last_chance()
    assert POINTS_LAST_CHANCE in get_found_point_types(game_stats)