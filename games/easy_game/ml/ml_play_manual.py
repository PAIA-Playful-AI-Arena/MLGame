import random
import pygame


class MLPlay:
    def __init__(self):
        print("Initial ml script")

    def update(self, scene_info: dict, keyboard):
        """
        Generate the command according to the received scene information
        """
        # print("AI received data from game :", json.dumps(scene_info))
        # print(scene_info)
        actions = ["UP", "DOWN", "LEFT", "RIGHT"]
        # TODO assert keyboard

        if pygame.K_w in keyboard:
            return ["UP"]
        elif pygame.K_s in keyboard:
            return ["DOWN"]
        elif pygame.K_a in keyboard:
            return ["LEFT"]
        elif pygame.K_d in keyboard:
            return ["RIGHT"]
        else:
            return ["NONE"]
        # return random.sample(actions, 1)

    def reset(self):
        """
        Reset the status
        """
        print("reset ml script")
        pass
