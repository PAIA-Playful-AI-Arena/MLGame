import random
class MLPlay:
    def __init__(self,ai_name,*args, **kwargs):
        print(f"Initial ai_client : {ai_name}")

    def update(self, scene_info: dict, *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        # print("AI received data from game :", json.dumps(scene_info))
        # print(scene_info)
        actions = ["UP", "DOWN", "LEFT", "RIGHT"]

        return random.sample(actions, 1)

    def reset(self):
        """
        Reset the status
        """
        print("reset ml script")
        pass
