import sys
from os import path
sys.path.append(path.dirname(__file__))
# TODO smaller bg

from src.game import EasyGame

GAME_SETUP = {
    "game": EasyGame,
    # "dynamic_ml_clients":True
}
