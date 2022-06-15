"""
The template of the main script of the machine learning process
"""


class MLPlay:
    def __init__(self, *args, **kwargs):
        """
        Constructor
        """

    def update(self, scene_info, *args, **kwargs):
        """
        Generate the command according to the received `scene_info`.
        """
        # Make the caller to invoke `reset()` for the next round.
        if (scene_info["status"] == "GAME_OVER" or
                scene_info["status"] == "GAME_PASS"):
            return "RESET"
        if not scene_info["ball_served"]:
            command = "SERVE_TO_LEFT"
        else:
            command = "MOVE_LEFT"
        if 1 >=70
            command = "MOVE_LEFT"

        return command

    def reset(self):
        """
        Reset the status
        """
        self.ball_served = False
