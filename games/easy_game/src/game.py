import time
from os import path

import pygame

from mlgame.game.paia_game import PaiaGame, GameResultState, GameStatus
from mlgame.utils.enum import get_ai_name
from mlgame.view.decorator import check_game_progress, check_game_result
from mlgame.view.view_model import create_text_view_data, create_asset_init_data, create_image_view_data, Scene, \
    create_scene_progress_data
from .game_object import Ball, Food

ASSET_PATH = path.join(path.dirname(__file__), "../asset")


class EasyGame(PaiaGame):
    """
    This is a Interface of a game
    """

    def __init__(self, time_to_play, total_point_count, score, color, *args, **kwargs):
        super().__init__(user_num=1)
        self.game_result_state = GameResultState.FAIL
        self.scene = Scene(width=800, height=600, color="#4FC3F7", bias_x=0, bias_y=0)
        print(color)
        self.ball = Ball("#" + color)
        self.foods = pygame.sprite.Group()
        self.score = 0
        self.score_to_win = score
        self._create_foods(total_point_count)
        self._begin_time = time.time()
        self._timer = 0
        self.frame_count = 0
        self.time_limit = time_to_play

    def update(self, commands):
        # handle command
        ai_1p_cmd = commands[get_ai_name(0)]
        if ai_1p_cmd is not None:
            action = ai_1p_cmd[0]
        else:
            action = "NONE"
        # print(ai_1p_cmd)
        self.ball.update(action)

        # update sprite
        self.foods.update()

        # handle collision
        hits = pygame.sprite.spritecollide(self.ball, self.foods, True, pygame.sprite.collide_rect_ratio(0.8))
        if hits:
            self.score += len(hits)
            self._create_foods(len(hits))
        self._timer = round(time.time() - self._begin_time, 3)

        self.frame_count += 1
        # self.draw()

        if not self.is_running:
            return "QUIT"

    def get_data_from_game_to_player(self):
        """
        send something to game AI
        we could send different data to different ai
        """
        to_players_data = {}
        foods_data = []
        for food in self.foods:
            foods_data.append({"x": food.rect.x, "y": food.rect.y})
        data_to_1p = {
            "frame": self.frame_count,
            "ball_x": self.ball.rect.centerx,
            "ball_y": self.ball.rect.centery,
            "foods": foods_data,
            "score": self.score,
            "status": self.get_game_status()
        }

        to_players_data[get_ai_name(0)] = data_to_1p
        # should be equal to config. GAME_SETUP["ml_clients"][0]["name"]

        return to_players_data

    def get_game_status(self):

        if self.is_running:
            status = GameStatus.GAME_ALIVE
        elif self.score > self.score_to_win:
            status = GameStatus.GAME_PASS
        else:
            status = GameStatus.GAME_OVER
        return status

    def reset(self):
        pass

    @property
    def is_running(self):
        return self.frame_count < self.time_limit

    def get_scene_init_data(self):
        """
        Get the initial scene and object information for drawing on the web
        """
        # TODO add music or sound
        bg_path = path.join(ASSET_PATH, "img/background.jpg")
        background = create_asset_init_data(
            "background", 800, 600, bg_path,
            github_raw_url="https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/easy_game/main/asset/img/background.jpg")
        scene_init_data = {"scene": self.scene.__dict__,
                           "assets": [
                               background
                           ],
                           # "audios": {}
                           }
        return scene_init_data

    @check_game_progress
    def get_scene_progress_data(self):
        """
        Get the position of game objects for drawing on the web
        """
        foods_data = []
        for food in self.foods:
            foods_data.append(food.game_object_data)
        game_obj_list = [self.ball.game_object_data]
        game_obj_list.extend(foods_data)
        backgrounds = [create_image_view_data("background", 0, 0, 800, 600)]
        foregrounds = [create_text_view_data(f"Score = {str(self.score)}", 650, 50, "#FF0000", "24px Arial BOLD")]
        toggle_objs = [create_text_view_data(f"Timer = {str(self._timer)} s", 650, 100, "#FFAA00", "24px Arial")]
        scene_progress = create_scene_progress_data(frame=self.frame_count, background=backgrounds,
                                                    object_list=game_obj_list,
                                                    foreground=foregrounds, toggle=toggle_objs)
        return scene_progress

    @check_game_result
    def get_game_result(self):
        """
        send game result
        """
        if self.get_game_status() == GameStatus.GAME_PASS:
            self.game_result_state = GameResultState.FINISH
        return {"frame_used": self.frame_count,
                "state": self.game_result_state,
                "attachment": [
                    {
                        "player": get_ai_name(0),
                        "rank": 1,
                        "score": self.score
                    }
                ]

                }

    def get_keyboard_command(self):
        """
        Define how your game will run by your keyboard
        """
        cmd_1p = []
        key_pressed_list = pygame.key.get_pressed()
        if key_pressed_list[pygame.K_UP]:
            cmd_1p.append("UP")
        elif key_pressed_list[pygame.K_DOWN]:
            cmd_1p.append("DOWN")
        elif key_pressed_list[pygame.K_LEFT]:
            cmd_1p.append("LEFT")
        elif key_pressed_list[pygame.K_RIGHT]:
            cmd_1p.append("RIGHT")
        else:
            cmd_1p.append("NONE")
        return {get_ai_name(0): cmd_1p}

    def _create_foods(self, count: int = 5):
        for i in range(count):
            # add food to group
            food = Food(self.foods)
        pass
