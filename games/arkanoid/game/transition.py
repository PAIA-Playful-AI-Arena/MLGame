from mlgame.communication.game import send_to_transition

class TransitionServer:
    """Pass the scene info received to the message server
    """
    def __init__(self):
        """Constructor
        """
        pass

    def send_game_info(self):
        """Send the information of the game to the message server
        """
        info_dict = {
            "scene": {
                "size": [200, 500]
            },
            "game_object": [
                { "name": "ball", "size": [5, 5], "color": [44, 185, 214] },
                { "name": "platform", "size": [40, 5], "color": [66, 226, 126] },
                { "name": "brick", "size": [25, 10], "color": [244, 158, 66] },
            ]
        }

        send_to_transition({
            "type": "game_info",
            "data": info_dict,
        })

    def send_scene_info(self, scene_info, frame_delayed: int):
        """Send the scene_info to the message server
        """
        status_dict = {
            "frame": scene_info.frame,
            "frame_delayed": [frame_delayed],
        }
        gameobject_dict = {
            "ball": [scene_info.ball],
            "platform": [scene_info.platform],
            "brick": scene_info.bricks
        }

        send_to_transition({
            "type": "game_progress",
            "data": {
                "status": status_dict,
                "game_object": gameobject_dict,
            }
        })

    def send_game_result(self, scene_info, frame_delayed: int):
        """Send the game result to the message server
        """
        game_result_dict = {
            "frame_used": scene_info.frame,
            "frame_delayed": [frame_delayed],
            "result": [scene_info.status],
            "brick_remain": len(scene_info.bricks),
        }

        send_to_transition({
            "type": "game_result",
            "data": game_result_dict,
        })
