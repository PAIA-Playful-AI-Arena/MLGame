"""
The template of the main script of the machine learning process
"""
import os, pickle
import numpy as np

class MLPlay:
    def __init__(self):
        """
        Constructor
        """
        self.ball_served = False
        self.previous_ball = (0, 0)
        # Need scikit-learn==0.22.2 
        with open(os.path.join(os.path.dirname(__file__),'model.pickle'), 'rb') as f:
            self.model = pickle.load(f)
            
    def update(self, scene_info):
        """
        Generate the command according to the received `scene_info`.
        """
        # Make the caller to invoke `reset()` for the next round.
        if (scene_info["status"] == "GAME_OVER" or
            scene_info["status"] == "GAME_PASS"):
            return "RESET"

        if not self.ball_served:
            self.ball_served = True
            command = "SERVE_TO_LEFT"
        else:
            Ball_x = scene_info["ball"][0]
            Ball_y = scene_info["ball"][1]
            Ball_speed_x = scene_info["ball"][0] - self.previous_ball[0]
            Ball_speed_y = scene_info["ball"][1] - self.previous_ball[1]
            Platform = scene_info["platform"][0]
            if Ball_speed_x > 0 :
                if Ball_speed_y > 0:  Direction = 0
                else :  Direction = 1
            else :
                if Ball_speed_y > 0:  Direction = 2
                else :  Direction = 3
            x = np.array([Ball_x, Ball_y, Direction, Ball_speed_x, Ball_speed_y, Platform]).reshape((1, -1))
            y = self.model.predict(x)
            if y == 0: command = "NONE"
            elif y == -1: command = "MOVE_LEFT"
            elif y == 1: command = "MOVE_RIGHT"
            
        self.previous_ball = scene_info["ball"]
        return command

    def reset(self):
        """
        Reset the status
        """
        self.ball_served = False
