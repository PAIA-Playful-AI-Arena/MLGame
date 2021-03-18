"""
The template of the script for the machine learning process in game pingpong
"""
import random
import time


class MLPlay:
    def __init__(self, side):
        """
        Constructor

        @param side A string "1P" or "2P" indicates that the `MLPlay` is used by
               which side.
        """
        self.ball_served = False
        self.side = side

    def update(self, scene_info):
        """
        Generate the command according to the received scene information
        """
        if scene_info["status"] != "GAME_ALIVE":
            return "RESET"
        will_delay = random.randint(1, 101) > 90
        if will_delay:
            time.sleep(0.1)
        return random.choice(("MOVE_LEFT", "MOVE_RIGHT"))

    def reset(self):
        """
        Reset the status
        """
        self.ball_served = False
