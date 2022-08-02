"""
The template of the script for the machine learning process in game pingpong
"""


class MLPlay:
    def __init__(self, ai_name: str, *args, **kwargs):
        """
        Constructor

        @param side A string "1P" or "2P" indicates that the `MLPlay` is used by
               which side.
        """
        self.ball_served = False
        self.side = ai_name
        self.game_params = kwargs['game_params']
        # self.game_params = game_params
        print(self.game_params)

    def update(self, scene_info, *args, **kwargs) -> str:
        """
        Generate the command according to the received scene information
        """
        if scene_info["status"] != "GAME_ALIVE":
            return "RESET"

        if not self.ball_served:
            self.ball_served = True
            return "SERVE_TO_LEFT"
        else:
            if self.side == "1P":
                if scene_info["ball_speed"][1] > 0:  # 球正在向下 # ball goes down
                    x = (scene_info["platform_1P"][1] - scene_info["ball"][1]) // scene_info["ball_speed"][1]  # 幾個frame以後會需要接  # x means how many frames before catch the ball
                    pred = scene_info["ball"][0] + (
                            scene_info["ball_speed"][0] * x)  # 預測最終位置 # pred means predict ball landing site
                    bound = pred // 200  # Determine if it is beyond the boundary
                    if bound > 0:  # pred > 200 # fix landing position
                        if bound % 2 == 0:
                            pred = pred - bound * 200
                        else:
                            pred = 200 - (pred - 200 * bound)
                    elif bound < 0:  # pred < 0
                        if bound % 2 == 1:
                            pred = abs(pred - (bound + 1) * 200)
                        else:
                            pred = pred + (abs(bound) * 200)
                else:  # 球正在向上
                    pred = 100
                if (pred - 10) < scene_info["platform_1P"][0] + 20 < (pred + 10):
                    return "NONE"
                elif scene_info["platform_1P"][0] + 20 <= (pred - 10):
                    return "MOVE_RIGHT"  # goes right
                else:
                    return "MOVE_LEFT"  # goes left

            elif self.side == "2P":
                if scene_info["ball_speed"][1] > 0:
                    pred = 100
                else:
                    x = (scene_info["platform_2P"][1] + 30 - scene_info["ball"][1]) // scene_info["ball_speed"][1]
                    pred = scene_info["ball"][0] + (scene_info["ball_speed"][0] * x)
                    bound = pred // 200
                    if (bound > 0):
                        if (bound % 2 == 0):
                            pred = pred - bound * 200
                        else:
                            pred = 200 - (pred - 200 * bound)
                    elif (bound < 0):
                        if bound % 2 == 1:
                            pred = abs(pred - (bound + 1) * 200)
                        else:
                            pred = pred + (abs(bound) * 200)
                if (pred - 10) < scene_info["platform_2P"][0] + 20 < (pred + 10):
                    return "NONE"  # NONE
                elif scene_info["platform_2P"][0] + 20 <= (pred - 10):
                    return "MOVE_RIGHT"  # goes right
                else:
                    return "MOVE_LEFT"  # goes left

    def reset(self):
        """
        Reset the status
        """
        self.ball_served = False
