"""
The template of the script for the machine learning process in game pingpong
"""


class MLPlay:
    def __init__(self, side):
        """
        Constructor

        @param side A string "1P" or "2P" indicates that the `MLPlay` is used by
               which side.
        """
        self.ball_served = False
        self.side = side
        self.frame_count = 0

    def update(self, scene_info, *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        if scene_info["status"] != "GAME_ALIVE":
            return "RESET"
        self.frame_count += 1
        if not self.ball_served:
            self.ball_served = True
            return "SERVE_TO_RIGHT"
        else:
            if self.side == "2P":
                import unexisted_lib as lib

            return "MOVE_LEFT"

    def reset(self):
        """
        Reset the status
        """
        print("reset " + self.side)
        self.ball_served = False
