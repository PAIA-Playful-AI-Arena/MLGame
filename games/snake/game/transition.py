from mlgame.communication.game import send_to_transition

class TransitionServer:
    def send_game_info(self):
        info_dict = {
            "scene": {
                "size": [300, 300]
            },
            "game_object": [
                { "name": "snake_head", "size": [10, 10], "color": [31, 204, 42] },
                { "name": "snake_body", "size": [10, 10], "color": [255, 255, 255] },
                { "name": "food", "size": [10, 10], "color": [232, 54, 42] },
            ]
        }

        send_to_transition({
            "type": "game_info",
            "data": info_dict
        })

    def send_game_progress(self, scene_info, frame_delayed):
        progress_dict = {
            "status": {
                "frame": scene_info.frame,
                "frame_delayed": [frame_delayed]
            },
            "game_object": {
                "snake_head": [scene_info.snake_head],
                "snake_body": scene_info.snake_body,
                "food": [scene_info.food]
            }
        }

        send_to_transition({
            "type": "game_progress",
            "data": progress_dict
        })

    def send_game_result(self, scene_info, frame_delayed, score):
        result_dict = {
            "frame_used": scene_info.frame,
            "frame_delayed": [frame_delayed],
            "result": ["GAME_OVER"],
            "score": score
        }

        send_to_transition({
            "type": "game_result",
            "data": result_dict
        })
