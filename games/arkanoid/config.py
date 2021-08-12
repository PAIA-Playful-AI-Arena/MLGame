from os import path

from mlgame.utils.parse_config import read_json_file, parse_config
from .src.game import Arkanoid

config_file = path.join(path.dirname(__file__), "game_config.json")

config_data = read_json_file(config_file)
GAME_VERSION = config_data["version"]
GAME_PARAMS = parse_config(config_data)

GAME_SETUP = {
    "game": Arkanoid,
    "ml_clients": Arkanoid.ai_clients()
}
