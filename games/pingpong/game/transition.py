from mlgame.communication.game import send_to_transition

class TransitionServer:
    """
    Pass the scene info received to the message server
    """
    def __init__(self):
        """
        Constructor
        """
        pass

    def send_game_info(self):
        """
        Send the game information to the message server
        """
        info_dict = {
            "scene": {
                "size": [200, 500],
            },
            "game_object": [
                { "name": "platform_1P", "size": [40, 30], "color": [84, 149, 255] },
                { "name": "platform_2P", "size": [40, 30], "color": [219, 70, 92] },
                { "name": "blocker", "size": [30, 20], "color": [213, 224, 0] },
                { "name": "ball", "size": [5, 5], "color": [66, 226, 126] },
            ]
        }

        send_to_transition({
            "type": "game_info",
            "data": info_dict,
        })

    def send_scene_info(self, scene_info, frame_delayed):
        """
        Send the scene info to the message server
        """
        status_dict = {
            "frame": scene_info["frame"],
            "frame_delayed": frame_delayed,
            "ball_speed": scene_info["ball_speed"],
        }
        gameobject_dict = {
            "ball": [scene_info["ball"]],
            "platform_1P": [scene_info["platform_1P"]],
            "platform_2P": [scene_info["platform_2P"]],
        }
        if scene_info.get("blocker"):
            gameobject_dict["blocker"] = [scene_info["blocker"]]

        send_to_transition({
            "type": "game_progress",
            "data": {
                "status": status_dict,
                "game_object": gameobject_dict,
            }
        })

    def send_game_result(self, scene_info, frame_delayed, final_score):
        """
        Send the game result to the message server
        """
        if final_score[0] > final_score[1]:
            status = ["GAME_PASS", "GAME_OVER"]
        else:
            status = ["GAME_OVER", "GAME_PASS"]

        game_result_dict = {
            "frame_used": scene_info["frame"],
            "frame_delayed": frame_delayed,
            "result": status,
            "ball_speed": scene_info["ball_speed"],
        }

        send_to_transition({
            "type": "game_result",
            "data": game_result_dict,
        })
