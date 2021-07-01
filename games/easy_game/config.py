GAME_VERSION = "1.1"
GAME_PARAMS = {
    "()": {
        "prog": "easy-game",
        "game_usage": "%(prog)s <difficulty> <level>"
    },
    "difficulty": {
        "choices": ("EASY", "NORMAL"),
        "metavar": "difficulty",
        "help": "Specify the game style. Choices: %(choices)s"
    },
    "level": {
        "type": int,
        "help": "Specify the level map"
    }
}

from .src.game import EasyGame


# TODO
# should be equal to config. GAME_SETUP["ml_clients"][0]["name"]

GAME_SETUP = {
    "game": EasyGame,
    "ml_clients": [
        { "name": "ml_1P" }
    ]
}
