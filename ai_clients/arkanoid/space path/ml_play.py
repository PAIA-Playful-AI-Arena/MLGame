"""
The template of the main script of the machine learning process
"""
import random


class MLPlay:
    def __init__(self,ai_name,*args, **kwargs):
        """
        Constructor
        """
        self.ball_served = False
        self.previous_ball = (0, 0)
        self.serve_pos = random.randint(1, 175)
        print(ai_name)
        print(kwargs)

    def update(self, scene_info,*args, **kwargs):
        """
        Generate the command according to the received `scene_info`.
        """
        # Make the caller to invoke `reset()` for the next round.
        if (scene_info["status"] == "GAME_OVER" or
                scene_info["status"] == "GAME_PASS"):
            return "RESET"
        current_ball = scene_info["ball"]
        if not self.ball_served:
            if current_ball[0] > self.serve_pos:
                command = "MOVE_LEFT"
            else:
                command = "MOVE_RIGHT"
            if abs(current_ball[0]-self.serve_pos) < 7:
                self.ball_served = True
                command = random.choice(
                    ["SERVE_TO_RIGHT", "SERVE_TO_LEFT"])  # 發球
            self.previous_ball = scene_info["ball"]
        else:
            # rule code
            direction = self.getDirection(
                self.previous_ball, scene_info["ball"])

            result = 100
            if direction <= 2:  # 球正在往上
                pass
            else:  # 球正在往下，判斷球的落點
                result = self.predictFalling_x(
                    self.previous_ball, current_ball)
                # 判斷command
            command = self.getCommand(scene_info["platform"][0], result)
            return "MOVE_RIGHT"
        self.previous_ball = scene_info["ball"]
        return command


    def getDirection(self, previous_ball, current_ball):
        """
        result
        1 : top right
        2 : top left
        3 : bottom left
        4 : bottom right
        """
        if previous_ball[1] > current_ball[1]:
            if previous_ball[0] > current_ball[0]:
                return 2
            else:
                return 1
        else:
            if previous_ball[0] > current_ball[0]:
                return 3
            else:
                return 4

    def predictFalling_x(self, previous_ball, current_ball):
        direction_x = current_ball[0] - previous_ball[0]
        direction_y = current_ball[1] - previous_ball[1]
        ball_x_end = 0
        # y = mx + c
        if direction_y > 0:
            m = direction_y / direction_x
            c = current_ball[1] - m*current_ball[0]
            ball_x_end = (400 - c)/m
        else:
            ball_x_end = 100
        while ball_x_end < 0 or ball_x_end > 200:
            if ball_x_end < 0:
                ball_x_end = -ball_x_end
            elif ball_x_end > 200:
                ball_x_end = 400-ball_x_end
        # print(ball_x_end)
        return ball_x_end

    def getCommand(self, platform_x, predict_x):
        if platform_x+20 - 5 > predict_x:
            return "MOVE_LEFT"
        elif platform_x+20 + 5 < predict_x:
            return "MOVE_RIGHT"
        else:
            return "NONE"

    def reset(self):
        """
        Reset the status
        """
        self.ball_served = False
        self.serve_pos = random.randint(1, 175)
