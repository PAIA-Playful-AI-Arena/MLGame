
from os import path

from mlgame.utils.parse_config import read_json_file, parse_config
from .src.game import EasyGame

config_file = path.join(path.dirname(__file__), "game_config.json")


config_data = read_json_file(config_file)
GAME_VERSION = config_data["version"]
GAME_PARAMS = parse_config(config_data)

# will be equal to config. GAME_SETUP["ml_clients"][0]["name"]

GAME_SETUP = {
    "game": EasyGame,
    "ml_clients": EasyGame.ai_clients(),
    # "dynamic_ml_clients":True
}
