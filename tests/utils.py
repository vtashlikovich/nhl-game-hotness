import json

def get_found_point_types(game_stats):
    return [k['code'] for k in game_stats.getPoints()]

def load_game(game_id, file_postfix=''):
    result = None
    with open('samples/' + str(game_id) + file_postfix + '.json') as game_file:
        result = json.loads(game_file.read())
    return result