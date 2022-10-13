import os

TIMEOUT = int(os.getenv("WS_TIMEOUT", 30))
WS_WAIT_GAME_TIMEOUT = int(os.getenv("WS_WAIT_GAME_TIMEOUT", 15))
