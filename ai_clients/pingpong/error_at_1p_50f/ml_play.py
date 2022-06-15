"""
The template of the script for the machine learning process in game pingpong
"""


class MLPlay:
    def __init__(self, ai_name,*args,**kwargs):
        """
        Constructor

        @param side A string "1P" or "2P" indicates that the `MLPlay` is used by
               which side.
        """
        self.ball_served = False
        self.side = ai_name
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
            if self.side == "1P" and self.frame_count >= 50:
                k = scene_info["not_existed_key"]
            return "MOVE_LEFT"

    def reset(self):
        """
        Reset the status
        """
        print("reset " + self.side)
        self.ball_served = False
