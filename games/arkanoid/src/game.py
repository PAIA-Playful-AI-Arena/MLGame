import random
import pygame
from mlgame.gamedev.game_interface import PaiaGame, GameResultState, GameStatus
from mlgame.view.test_decorator import check_game_progress, check_game_result
from mlgame.view.view_model import create_text_view_data, Scene
from .game_object import Ball, Platform, Brick, HardBrick, PlatformAction, SERVE_BALL_ACTIONS


class Arkanoid(PaiaGame):
    def __init__(self, difficulty, level):
        super().__init__()
        self.frame_count = 0
        self.level = level
        self.difficulty = difficulty
        self.game_result_state = GameResultState.FAIL
        self.ball_served = False
        self.scene = Scene(width=200, height=500, color="#000000", bias_x=0, bias_y=0)
        self._create_init_scene()

    def update(self, commands):
        ai_1p_cmd = commands[self.ai_clients()[0]["name"]]
        command = (PlatformAction(ai_1p_cmd)
                   if ai_1p_cmd in PlatformAction.__members__ else PlatformAction.NONE)

        self.frame_count += 1
        self._platform.move(command)

        if not self.ball_served:
            # Force to serve the ball after 150 frames
            if (self.frame_count >= 150 and
                    command not in SERVE_BALL_ACTIONS):
                command = random.choice(SERVE_BALL_ACTIONS)

            self._wait_for_serving_ball(command)
        else:
            self._ball_moving()

        if not self.is_running:
            return "RESET"

    def _wait_for_serving_ball(self, platform_action: PlatformAction):
        self._ball.stick_on_platform(self._platform.rect.centerx)

        if platform_action in SERVE_BALL_ACTIONS:
            self._ball.serve(platform_action)
            self.ball_served = True

    def _ball_moving(self):
        self._ball.move()

        self._ball.check_hit_brick(self._group_brick)
        self._ball.check_bouncing(self._platform)

    def game_to_player_data(self):
        to_players_data = {}
        data_to_1p = {
            "frame": self.frame_count,
            "status": self.get_game_status(),
            "ball": self._ball.pos,
            "platform": self._platform.pos,
            "bricks": [],
            "hard_bricks": []
        }

        for brick in self._group_brick:
            if isinstance(brick, HardBrick) and brick.hp == 2:
                data_to_1p["hard_bricks"].append(brick.pos)
            else:
                data_to_1p["bricks"].append(brick.pos)

        for ai_client in self.ai_clients():
            to_players_data[ai_client['name']] = data_to_1p

        return to_players_data

    def get_game_status(self):
        if len(self._group_brick) == 0:
            self._game_status = GameStatus.GAME_PASS
        elif self._ball.rect.top >= self._platform.rect.bottom:
            self._game_status = GameStatus.GAME_OVER
        else:
            self._game_status = GameStatus.GAME_ALIVE
        return self._game_status

    def reset(self):
        self.game_result_state = GameResultState.FAIL
        self.ball_served = False
        self.frame_count = 0
        self._create_init_scene()
        pass

    @property
    def is_running(self):
        return self.get_game_status() == GameStatus.GAME_ALIVE

    def get_scene_init_data(self):
        scene_init_data = {"scene": self.scene.__dict__,
                           "assets": [

                           ]
                           }
        return scene_init_data

    @check_game_progress
    def get_scene_progress_data(self):
        bricks_data = []
        lines = []
        for brick in self._group_brick:
            bricks_data.append(brick.get_object_data)
            lines.append(brick.get_line_data1)
            lines.append(brick.get_line_data2)

        game_obj_list = []
        for move in self._group_move:
            game_obj_list.append(move.get_object_data)

        game_obj_list.extend(bricks_data)
        game_obj_list.extend(lines)

        catch_ball_text = create_text_view_data("catching ball: " + str(self._ball.hit_platform_times), 1,
                                                self.scene.height - 21, "#FFFFFF", "18px Arial")
        foreground = [catch_ball_text]
        foreground.extend(lines)

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
    def get_game_result(self):
        if len(self._group_brick) == 0:
            self.game_result_state = GameResultState.FINISH
        return {
            "frame_used": self.frame_count,
            "state": self.game_result_state,
            "attachment": [
                {
                    "player": self.ai_clients()[0]['name'],
                    "brick_remain": len(self._brick_container),
                    "count_of_catching_ball": self._ball.hit_platform_times

                }
            ]

        }

    def get_keyboard_command(self):
        cmd_1p = "NONE"
        key_pressed_list = pygame.key.get_pressed()
        if key_pressed_list[pygame.K_a]:
            cmd_1p = "SERVE_TO_LEFT"
        elif key_pressed_list[pygame.K_d]:
            cmd_1p = "SERVE_TO_RIGHT"
        elif key_pressed_list[pygame.K_LEFT]:
            cmd_1p = "MOVE_LEFT"
        elif key_pressed_list[pygame.K_RIGHT]:
            cmd_1p = "MOVE_RIGHT"
        else:
            cmd_1p = "NONE"

        ai_1p = self.ai_clients()[0]["name"]

        return {ai_1p: cmd_1p}

    def _create_init_scene(self):
        '''
        初始遊戲畫面：
        1. 球
        2. 板子
        3. 磚塊
        '''
        self._create_moves()
        self._create_bricks(self.level)

    def _create_moves(self):
        self._group_move = pygame.sprite.RenderPlain()
        enable_slide_ball = False if self.difficulty == "EASY" else True
        self._ball = Ball((93, 395), pygame.Rect(0, 0, 200, 500), enable_slide_ball, self._group_move)
        self._platform = Platform((75, 400), pygame.Rect(0, 0, 200, 500), self._group_move)

    def _create_bricks(self, level: int):
        def get_coordinate_and_type(string):
            string = string.rstrip("\n").split(' ')
            return int(string[0]), int(string[1]), int(string[2])

        self._group_brick = pygame.sprite.RenderPlain()
        self._brick_container = []

        import os.path as path
        asset_path = path.join(path.dirname(__file__),'..','asset')

        level_file_path = path.join(asset_path, "level_data/{0}.dat".format(level))
        if not path.exists(level_file_path):
            print("level is not existed , turn to level 1")
            level_file_path = path.join(asset_path, "level_data/{0}.dat".format(1))

        with open(level_file_path, 'r') as input_file:
            offset_x, offset_y, _ = get_coordinate_and_type(input_file.readline())
            for input_pos in input_file:
                pos_x, pos_y, type = get_coordinate_and_type(input_pos.rstrip("\n"))
                BrickType = {
                    0: Brick,
                    1: HardBrick,
                }.get(type, Brick)

                brick = BrickType((pos_x + offset_x, pos_y + offset_y),
                                  self._group_brick)
                self._brick_container.append(brick)

    @staticmethod
    def ai_clients():
        """
        let MLGame know how to parse your ai,
        you can also use this names to get different cmd and send different data to each ai client
        """
        return [
            {"name": "1P"}
        ]
