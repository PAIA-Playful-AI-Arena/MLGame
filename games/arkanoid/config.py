from .src.game import Arkanoid
GAME_VERSION = "2.0.1"
GAME_PARAMS = {
    "()": {
        "prog": "arkanoid",
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



GAME_SETUP = {
    "game": Arkanoid,
    "ml_clients": Arkanoid.ai_clients()
}
