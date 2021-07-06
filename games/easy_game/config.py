from .src.game import EasyGame

GAME_VERSION = "1.1"
GAME_PARAMS = {
    "()": {
        "prog": "easy-game",
        "game_usage": "%(prog)s <param1> [param2] [param3]"
    },
    "param1": {
        "choices": ("EASY", "NORMAL"),
        "metavar": "param1",
        "help": "Specify the game style. Choices: %(choices)s"
    },
    "param2": {
        "type": int,
        "nargs": "?",
        "metavar": "param2",
        "default": 1,
        "help": ("[Optional] The score that the game will be exited "
                 "when either side reaches it.[default: %(default)s]")
    },
    "param3": {
        "nargs": "?",
        "metavar": "param3",
        "default": "blabla",
        "help": ("[Optional] The score that the game will be exited "
                 "when either side reaches it.[default: %(default)s]")
    }
}

# will be equal to config. GAME_SETUP["ml_clients"][0]["name"]

GAME_SETUP = {
    "game": EasyGame,
    "ml_clients": EasyGame.ai_clients()
}