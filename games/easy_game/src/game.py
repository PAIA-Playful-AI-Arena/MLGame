import abc

import pygame

from mlgame.view_model import create_text_view_model
from .game_object import Scene, Ball, Food


class EasyGame():
    """
    This is a Interface of a game
    TODO constructor param should be equal to config
    """

    def __init__(self, difficulty, level):
        self.scene = Scene(width=800, height=600, color="#4FC3F7")
        self.running = True

        self.ball = Ball()
        self.foods = pygame.sprite.Group()
        self.score = 0
        self._create_foods()
        pass

    def update(self, commands):
        # hanndle command
        self.ball.update(commands["ml_1P"])

        # update sprite
        self.foods.update()

        # handle collision
        hits = pygame.sprite.spritecollide(self.ball, self.foods, True, pygame.sprite.collide_rect_ratio(0.8))

        self._create_foods(len(hits))
        self.score += len(hits)

        # self.draw()
        if not self.is_running:
            return "QUIT"

    def game_to_player_data(self):
        """
        send something to game AI
        we could send different data to different ai
        """
        foods_data = []
        for food in self.foods:
            foods_data.append({"x": food.rect.x, "y": food.rect.y})
        ml_1P = {
            "ball_x": self.ball.rect.centerx,
            "ball_y": self.ball.rect.centery,
            "foods": foods_data,
            "score": self.score
        }
        data = {"ml_1P": ml_1P}
        # TODO refactor
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
        # TODO add image
        scene_init_data = {"scene": self.scene.__dict__,
                           "assets": None,
                           # "audios": {}
                           }
        return scene_init_data

    def get_scene_progress_data(self):
        """
        Get the position of game objects for drawing on the web
        """
        foods_data = []
        for food in self.foods:
            foods_data.append(food.game_object_data)
        game_obj_list = [self.ball.game_object_data]
        game_obj_list.extend(foods_data)

        score_text = create_text_view_model("Score = " + str(self.score), 700, 100, "#000000")
        scene_progress = {
            # background view data will be draw first
            "background": [
                score_text
            ],
            # TODO  let player to turn on/off
            "toggle": [],
            # game object view data will be draw on screen by order , and it could be shifted by WASD
            "object_list": game_obj_list,
            # other information to display on web
            "user_info": [],
            # other information to display on web
            "game_sys_info": {}
        }
        return scene_progress

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

    def _create_foods(self, count: int = 5):
        for i in range(count):
            # add food to group
            food = Food(self.foods)
        pass
