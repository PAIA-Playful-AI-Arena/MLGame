import random

import pygame

from mlgame.gamedev.game_interface import PaiaGame, GameStatus, GameResultState
from mlgame.view.test_decorator import check_game_progress, check_game_result
from mlgame.view.view_model import create_text_view_data, Scene
from .game_object import (
    Ball, Blocker, Platform, PlatformAction, SERVE_BALL_ACTIONS
)

color_1P = (219, 70, 92)  # Red
color_2P = (84, 149, 255)  # Blue


class PingPong(PaiaGame):

    def __init__(self, difficulty, game_over_score):
        super().__init__()
        self._difficulty = difficulty
        self._score = [0, 0]
        self._game_over_score = game_over_score
        self._frame_count = 0
        self._game_status = GameStatus.GAME_ALIVE
        self._ball_served = False
        self._ball_served_frame = 0
        self.scene = Scene(width=200, height=500, color="#000000", bias_x=0, bias_y=0)
        self._create_init_scene()

    def _create_init_scene(self):
        self._draw_group = pygame.sprite.RenderPlain()

        enable_slice_ball = False if self._difficulty == "EASY" else True
        self._ball = Ball(pygame.Rect(0, 0, 200, 500), enable_slice_ball, self._draw_group)
        self._platform_1P = Platform((80, pygame.Rect(0, 0, 200, 500).height - 80),
                                     pygame.Rect(0, 0, 200, 500), "1P", color_1P, self._draw_group)
        self._platform_2P = Platform((80, 50),
                                     pygame.Rect(0, 0, 200, 500), "2P", color_2P, self._draw_group)

        if self._difficulty != "HARD":
            # Put the blocker at the end of the world
            self._blocker = Blocker(1000, pygame.Rect(0, 0, 200, 500), self._draw_group)
        else:
            self._blocker = Blocker(240, pygame.Rect(0, 0, 200, 500), self._draw_group)

        # Initialize the position of the ball
        self._ball.stick_on_platform(self._platform_1P.rect, self._platform_2P.rect)

    def update(self, commands):
        ai_1p_cmd = commands[self.ai_clients()[0]["name"]]
        ai_2p_cmd = commands[self.ai_clients()[1]["name"]]
        command_1P = (PlatformAction(ai_1p_cmd)
                      if ai_1p_cmd in PlatformAction.__members__ else PlatformAction.NONE)
        command_2P = (PlatformAction(ai_2p_cmd)
                      if ai_2p_cmd in PlatformAction.__members__ else PlatformAction.NONE)

        self._frame_count += 1
        self._platform_1P.move(command_1P)
        self._platform_2P.move(command_2P)
        self._blocker.move()

        if not self._ball_served:
            self._wait_for_serving_ball(command_1P, command_2P)
        else:
            self._ball_moving()

        if self.get_game_status() != GameStatus.GAME_ALIVE:
            if self._game_over(self.get_game_status()):
                self._print_result()
                self._game_status = GameStatus.GAME_OVER
                return "QUIT"
            return "RESET"

        if not self.is_running:
            return "QUIT"

    def _game_over(self, status):
        """
        Check if the game is over
        """
        if status == GameStatus.GAME_1P_WIN:
            self._score[0] += 1
        elif status == GameStatus.GAME_2P_WIN:
            self._score[1] += 1
        else:  # Draw game
            self._score[0] += 1
            self._score[1] += 1

        is_game_over = (self._score[0] == self._game_over_score or
                        self._score[1] == self._game_over_score)

        return is_game_over

    def _print_result(self):
        """
        Print the result
        """
        if self._score[0] > self._score[1]:
            win_side = "1P"
        elif self._score[0] == self._score[1]:
            win_side = "No one"
        else:
            win_side = "2P"

        print("{} wins! Final score: {}-{}".format(win_side, *self._score))

    def _wait_for_serving_ball(self, action_1P: PlatformAction, action_2P: PlatformAction):
        self._ball.stick_on_platform(self._platform_1P.rect, self._platform_2P.rect)

        target_action = action_1P if self._ball.serve_from_1P else action_2P

        # Force to serve the ball after 150 frames
        if (self._frame_count >= 150 and
                target_action not in SERVE_BALL_ACTIONS):
            target_action = random.choice(SERVE_BALL_ACTIONS)

        if target_action in SERVE_BALL_ACTIONS:
            self._ball.serve(target_action)
            self._ball_served = True
            self._ball_served_frame = self._frame_count

    def _ball_moving(self):
        # Speed up the ball every 200 frames
        if (self._frame_count - self._ball_served_frame) % 100 == 0:
            self._ball.speed_up()

        self._ball.move()
        self._ball.check_bouncing(self._platform_1P, self._platform_2P, self._blocker)

    def game_to_player_data(self) -> dict:
        to_players_data = {}
        scene_info = {
            "frame": self._frame_count,
            "status": self.get_game_status(),
            "ball": self._ball.pos,
            "ball_speed": self._ball.speed,
            "platform_1P": self._platform_1P.pos,
            "platform_2P": self._platform_2P.pos
        }

        if self._difficulty == "HARD":
            scene_info["blocker"] = self._blocker.pos
        else:
            scene_info["blocker"] = (0, 0)

        for ai_client in self.ai_clients():
            to_players_data[ai_client['name']] = scene_info

        return to_players_data

    def get_game_status(self):
        if self._ball.rect.top > self._platform_1P.rect.bottom:
            self._game_status = GameStatus.GAME_2P_WIN
        elif self._ball.rect.bottom < self._platform_2P.rect.top:
            self._game_status = GameStatus.GAME_1P_WIN
        elif abs(min(self._ball.speed, key=abs)) > 40:
            self._game_status = GameStatus.GAME_DRAW
        else:
            self._game_status = GameStatus.GAME_ALIVE

        return self._game_status

    def reset(self):
        print("reset pingpong")
        self._frame_count = 0
        self._game_status = GameStatus.GAME_ALIVE
        self._ball_served = False
        self._ball_served_frame = 0
        self._ball.reset()
        self._platform_1P.reset()
        self._platform_2P.reset()
        self._blocker.reset()

        # Initialize the position of the ball
        self._ball.stick_on_platform(self._platform_1P.rect, self._platform_2P.rect)

    @property
    def is_running(self):
        # print(self.get_game_status())
        return self._game_status != GameStatus.GAME_OVER

    def get_scene_init_data(self) -> dict:
        scene_init_data = {"scene": self.scene.__dict__, "assets": [

        ]}
        return scene_init_data

    @check_game_progress
    def get_scene_progress_data(self) -> dict:
        game_obj_list = []
        for obj in self._draw_group:
            game_obj_list.append(obj.get_object_data)

        create_1p_score = create_text_view_data("1P: " + str(self._score[0]),
                                                1,
                                                self.scene.height - 21,
                                                "#D6465C",
                                                "18px Arial"
                                                )
        create_2p_score = create_text_view_data("2P: " + str(self._score[1]),
                                                1,
                                                4,
                                                "#5495FF",
                                                "18px Arial"
                                                )
        create_speed_text = create_text_view_data("Speed: " + str(self._ball.speed),
                                                  self.scene.width - 120,
                                                  self.scene.height - 21,
                                                  "#FFFFFF",
                                                  "18px Arial"
                                                  )
        foreground = [create_1p_score, create_2p_score, create_speed_text]

        scene_progress = {
            "background": [],
            "object_list": game_obj_list,
            "toggle": [],
            "foreground": foreground,
            "user_info": [],
            "game_sys_info": {}
        }

        return scene_progress

    @check_game_result
    def get_game_result(self) -> dict:
        attachment = []
        if self._score[0] > self._score[1]:
            attachment = [{
                "player": self.ai_clients()[0]["name"],
                "rank": 1,
                "score": self._score[0],
                "status": "GAME_PASS",

                "ball_speed": self._ball.speed,
            },
                {
                    "player": self.ai_clients()[1]["name"],
                    "rank": 2,
                    "score": self._score[1],
                    "status": "GAME_OVER",
                    "ball_speed": self._ball.speed,

                },

            ]
        elif self._score[0] < self._score[1]:
            attachment = [{
                "player": self.ai_clients()[0]["name"],
                "rank": 2,
                "score": self._score[0],
                "status": "GAME_OVER",

                "ball_speed": self._ball.speed,
            },
                {
                    "player": self.ai_clients()[1]["name"],
                    "rank": 1,
                    "score": self._score[1],
                    "status": "GAME_PASS",
                    "ball_speed": self._ball.speed,

                },

            ]

        else:
            # TODO if ball_speed is to high should be draw

            attachment = [{
                "player": self.ai_clients()[0]["name"],
                "rank": 1,
                "score": self._score[0],
                "status": "GAME_DRAW",
                # "ball_speed": self._ball.speed,
            },
                {
                    "player": self.ai_clients()[1]["name"],
                    "rank": 1,
                    "score": self._score[1],
                    # "ball_speed": self._ball.speed,
                },

            ]
        return {
            "frame_used": self._frame_count,
            "state": GameResultState.FINISH,
            "attachment": attachment

        }

    def get_keyboard_command(self) -> dict:
        cmd_1P = ""
        cmd_2P = ""

        key_pressed_list = pygame.key.get_pressed()

        if key_pressed_list[pygame.K_PERIOD]:
            cmd_1P = "SERVE_TO_LEFT"
        elif key_pressed_list[pygame.K_SLASH]:
            cmd_1P = "SERVE_TO_RIGHT"
        elif key_pressed_list[pygame.K_LEFT]:
            cmd_1P = "MOVE_LEFT"
        elif key_pressed_list[pygame.K_RIGHT]:
            cmd_1P = "MOVE_RIGHT"
        else:
            cmd_1P = "NONE"

        if key_pressed_list[pygame.K_q]:
            cmd_2P = "SERVE_TO_LEFT"
        elif key_pressed_list[pygame.K_e]:
            cmd_2P = "SERVE_TO_RIGHT"
        elif key_pressed_list[pygame.K_a]:
            cmd_2P = "MOVE_LEFT"
        elif key_pressed_list[pygame.K_d]:
            cmd_2P = "MOVE_RIGHT"
        else:
            cmd_2P = "NONE"

        ai_1p = self.ai_clients()[0]["name"]
        ai_2p = self.ai_clients()[1]["name"]

        return {ai_1p: cmd_1P, ai_2p: cmd_2P}

    @staticmethod
    def ai_clients():
        """
        let MLGame know how to parse your ai,
        you can also use this names to get different cmd and send different data to each ai client
        """
        return [
            {"name": "ml_1P", "args": ("1P",)},
            {"name": "ml_2P", "args": ("2P",)}
        ]
