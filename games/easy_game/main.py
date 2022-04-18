import pygame
import sys

sys.path.append(r"../..")
from mlgame.view.view import PygameView
from mlgame.gamedev.generic import quit_or_esc
from src.game import EasyGame

FPS = 30
if __name__ == '__main__':
    pygame.init()
    game = EasyGame(time_to_play=1000, total_point_count=10, score=5, color="FF9800")
    scene_init_info_dict = game.get_scene_init_data()
    game_view = PygameView(scene_init_info_dict)
    frame_count = 0
    while game.is_running and not quit_or_esc():
        pygame.time.Clock().tick_busy_loop(FPS)
        commands = game.get_keyboard_command()
        game.update(commands)
        game_progress_data = game.get_scene_progress_data()
        game_view.draw(game_progress_data)
        frame_count += 1
        # print(frame_count)

    pygame.quit()
