from time import process_time
import pygame

import sys
sys.path.append(r"../..")

from mlgame.view.view import PygameView
from mlgame.gamedev.generic import quit_or_esc
from src.game import EasyGame

FPS = 30
if __name__ == '__main__':
    pygame.init()
    game = EasyGame(param1="NORMAL", param2=1, param3="blabla")
    # game = MazeCar.MazeCar(1, "MOVE_MAZE", 4, 120, 3, "OFF")
    # game = MazeCar.MazeCar(1, "PRACTICE", 6, 120, 5, "OFF")
    scene_init_info_dict = game.get_scene_init_data()
    game_view = PygameView(scene_init_info_dict)
    frame_count = 0
    while game.is_running and not quit_or_esc():
        pygame.time.Clock().tick_busy_loop(FPS)
        commands = game.get_keyboard_command()
        game_progress_data = game.get_scene_progress_data()
        game.update(commands)
        game_view.draw_screen()
        game_view.draw(game_progress_data)
        game_view.flip()
        frame_count += 1
        # print(frame_count)

    pygame.quit()
