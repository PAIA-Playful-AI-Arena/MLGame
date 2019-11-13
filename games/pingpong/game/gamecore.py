import pygame
from mlgame.utils.enum import StringEnum

from .gameobject import (
    Ball, Platform, PlatformAction
)

color_1P = (219, 70, 92)    # Red
color_2P = (84, 149, 255)    # Blue

class GameStatus(StringEnum):
    GAME_1P_WIN = "GAME_1P_WIN"
    GAME_2P_WIN = "GAME_2P_WIN"
    GAME_ALIVE = "GAME_ALIVE"

class SceneInfo:
    """
    The data structure for storing the information of the scene

    `command_1P` and `command_2P` are filled after receiving the command
    from the ml process. Note that these two fields cannot check if
    the ml process is delayed or not.

    @var frame The frame number of the game
    @var status The status of the game. It will be the "value" (not "name")
         of one of the member of the GameStatus.
    @var ball An (x, y) tuple. The position of the ball.
    @var ball_speed A positive integer. The speed of the ball.
    @var platform_1P An (x, y) tuple. The position of the platform of 1P
    @var platform_2P An (x, y) tuple. The position of the platform of 2P
    @var command_1P The command for platform_1P in this frame. It will be the "value"
         (not "name") of one of the member of the PlatformAction.
    @var command_2P The command for platform_2P in this frame. Similar to `command_1P`.
    """
    def __init__(self):
        # These fields will be filled before being sent to the ml process
        self.frame = None
        self.status = None
        self.ball = None
        self.ball_speed = None
        self.platform_1P = None
        self.platform_2P = None

        # These fields will be filled after receiving the command
        # from the ml process
        self.command_1P = PlatformAction.NONE.value
        self.command_2P = PlatformAction.NONE.value

    def __str__(self):
        output_str = \
            "# Frame {}\n".format(self.frame) + \
            "# Status {}\n".format(self.status) + \
            "# Ball {}\n".format(self.ball) + \
            "# Ball_speed {}\n".format(self.ball_speed) + \
            "# Platform_1P {}\n".format(self.platform_1P) + \
            "# Platform_2P {}\n".format(self.platform_2P) + \
            "# Command_1P {}\n".format(self.command_1P) + \
            "# Command_2P {}".format(self.command_2P)

        return output_str

class Scene:
    area_rect = pygame.Rect(0, 0, 200, 500)

    def __init__(self, to_create_surface: bool):
        self._to_create_surface = to_create_surface
        self._frame_count = 0
        self._game_status = GameStatus.GAME_ALIVE

        self._create_scene()
        self.reset()

    def _create_scene(self):
        self._draw_group = pygame.sprite.RenderPlain()
        self._ball = Ball(Scene.area_rect, self._draw_group)
        self._platform_1P = Platform((80, Scene.area_rect.height - 80), \
            Scene.area_rect, self._draw_group)
        self._platform_2P = Platform((80, 50), \
            Scene.area_rect, self._draw_group)

        if self._to_create_surface:
            self._ball.create_surface()
            self._platform_1P.create_surface("1P", color_1P)
            self._platform_2P.create_surface("2P", color_2P)

    def reset(self):
        self._frame_count = 0
        self._game_status = GameStatus.GAME_ALIVE
        self._ball.reset()
        self._platform_1P.reset()
        self._platform_2P.reset()

    def update(self, \
        move_action_1P: PlatformAction, move_action_2P: PlatformAction):
        self._frame_count += 1

        # Speed up the ball every 200 frames
        if self._frame_count % 200 == 0:
            self._ball.speed_up()

        self._ball.move()
        self._platform_1P.move(move_action_1P)
        self._platform_2P.move(move_action_2P)

        self._ball.check_bouncing(self._platform_1P, self._platform_2P)

        if self._ball.rect.top > self._platform_1P.rect.bottom:
            self._game_status = GameStatus.GAME_2P_WIN
        elif self._ball.rect.bottom < self._platform_2P.rect.top:
            self._game_status = GameStatus.GAME_1P_WIN
        else:
            self._game_status = GameStatus.GAME_ALIVE

        return self._game_status

    def draw_gameobjects(self, surface):
        self._draw_group.draw(surface)

    def get_scene_info(self) -> SceneInfo:
        """
        Get the scene information
        """
        scene_info = SceneInfo()
        scene_info.frame = self._frame_count
        scene_info.status = self._game_status.value
        scene_info.ball = self._ball.pos
        scene_info.ball_speed = abs(self._ball._speed[0])
        scene_info.platform_1P = self._platform_1P.pos
        scene_info.platform_2P = self._platform_2P.pos

        return scene_info
