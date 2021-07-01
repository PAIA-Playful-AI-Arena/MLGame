import abc

import pygame
from .game_object import Scene, Ball


class EasyGame():
    """
    This is a Interface of a game
    TODO constructor param should be equal to config
    """

    def __init__(self, difficulty, level):
        self.scene = Scene(width=800, height=600, color="#4FC3F7")
        self.running = True

        self.ball = Ball()

        pass

    def update(self, commands):
        # hanndle command
        self.ball.update(commands["ml_1P"])
        # handle collision
        # update sprite

        # self.draw()
        if not self.is_running:
            return "QUIT"

    def game_to_player_data(self):
        """
        send something to game AI
        we could send different data to different ai
        """
        ml_1P = {
            "ball_x": self.ball.rect.centerx,
            "ball_y": self.ball.rect.centery,
        }
        data = {"ml_1P": ml_1P}
        # TODO
        # should be equal to config. GAME_SETUP["ml_clients"][0]["name"]

        return data

    def reset(self):
        pass

    @property
    def is_running(self):
        return self.running

    def get_scene_init_data(self):
        """
        Get the initial scene and object information for drawing on the web
        """

        scene_init_data = {"scene": self.scene.__dict__,
                           "assets": None,
                           # "audios": {}
                           }
        return scene_init_data

    def get_game_progress(self):
        """
        Get the position of game objects for drawing on the web
        """
        game_progress = {
            "game_background": [],
            "game_object_list": [
                self.ball.game_object_data
            ],
            "game_user_info": [],
            "game_sys_info": {}
        }
        return game_progress

    def get_game_result(self):
        """
        send game result
        """
        return {"frame_used": 1,
                # "result": result, # ["1P:7s", "2P:5s"]
                "ranks": []  # by score
                }

        pass

    def get_keyboard_command(self):
        """
        Define how your game will run by your keyboard
        """
        cmd_1P = []
        cmd_2P = []
        key_pressed_list = pygame.key.get_pressed()
        if key_pressed_list[pygame.K_UP]:
            cmd_1P.append("UP")
        if key_pressed_list[pygame.K_DOWN]:
            cmd_1P.append("DOWN")

        if key_pressed_list[pygame.K_LEFT]:
            cmd_1P.append("LEFT")

        if key_pressed_list[pygame.K_RIGHT]:
            cmd_1P.append("RIGHT")

        return {"ml_1P": cmd_1P,
                "ml_2P": cmd_2P}
