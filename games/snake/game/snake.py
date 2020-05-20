"""
The game execution for the manual mode
"""

import pygame

from .gamecore import Scene, GameStatus
from .gameobject import SnakeAction

class Snake:
    """
    The game execution manager
    """
    def __init__(self):
        self._scene = Scene()
        self._pygame_init()

    def _pygame_init(self):
        """
        Initialize the required pygame module
        """
        pygame.display.init()
        pygame.display.set_caption("Snake")
        self._screen = pygame.display.set_mode(
            (Scene.area_rect.width, Scene.area_rect.height + 25))

        self._clock = pygame.time.Clock()

        pygame.font.init()
        self._font = pygame.font.Font(None, 22)
        self._font_pos = (1, Scene.area_rect.width + 5)

    def update(self, cmd_list):
        """
        Update the game
        """
        # Get the command from the cmd_list
        command = cmd_list[0] if cmd_list else SnakeAction.NONE

        # Pass the command to the scene and get the status
        game_status = self._scene.update(command)
        self._draw_screen()

        # If the game is over, send the reset signal
        if game_status == GameStatus.GAME_OVER:
            print("Score: {}".format(self._scene.score))
            return "RESET"

    def _draw_screen(self):
        """
        Draw the scene to the display
        """
        self._screen.fill((50, 50, 50))
        self._screen.fill((0, 0, 0), Scene.area_rect)
        self._scene.draw_gameobjects(self._screen)

        # Draw score
        font_surface = self._font.render(
            "Score: {}".format(self._scene.score), True, (255, 255, 255))
        self._screen.blit(font_surface, self._font_pos)

        pygame.display.flip()

    def reset(self):
        """
        Reset the game

        This function is invoked when the executor receives the reset signal
        """
        self._scene.reset()

    def get_player_scene_info(self):
        """
        Get the scene information to be sent to the player
        """
        return self._scene.get_scene_info()
