import sys
import time

import pandas as pd

from mlgame.argument.cmd_argument import parse_cmd_and_get_arg_obj, create_cli_args_parser
from mlgame.argument.game_argument import create_game_arg_parser
from mlgame.core import errno
from mlgame.core.exceptions import GameProcessError
from mlgame.argument.model import GameConfig
from mlgame.gamedev.generic import quit_or_esc
from mlgame.gamedev.paia_game import PaiaGame
from mlgame.view.view import PygameView
import os.path as path


def test_play_easy_game_in_manual_mode():
    arg_str = f"-f 60 -1 " \
              f"{path.join(path.dirname(__file__), '../..', 'games', 'easy_game').__str__()}" \
              f" --score 10 --color FF9800 --time_to_play 600 --total_point 50"
    arg_obj = parse_cmd_and_get_arg_obj(arg_str)
    # parse game_folder/config.py
    game_config = GameConfig(arg_obj.game_folder.__str__())
    assert game_config
    param_parser = create_game_arg_parser(game_config.game_params)
    parsed_game_params = param_parser.parse_args(arg_obj.game_params)

    # init game
    # print(parsed_game_params)

    if arg_obj.is_manual:
        game_setup = game_config.game_setup
        game_cls = game_setup["game"]
        _frame_interval = 1 / arg_obj.fps
        try:
            game = game_cls(**parsed_game_params.__dict__)
            assert isinstance(game, PaiaGame), "Game " + str(game) + " should implement a abstract class : PaiaGame"

            scene_init_info_dict = game.get_scene_init_data()
            game_view = PygameView(scene_init_info_dict)
            while not quit_or_esc():
                scene_info_dict = game.game_to_player_data()
                time.sleep(_frame_interval)
                # pygame.time.Clock().tick_busy_loop(self._fps)
                cmd_dict = game.get_keyboard_command()
                # self._recorder.record(scene_info_dict, cmd_dict)

                result = game.update(cmd_dict)
                view_data = game.get_scene_progress_data()

                game_view.draw(view_data)

                if result == "RESET" or result == "QUIT":
                    scene_info_dict = game.game_to_player_data()
                    # self._recorder.record(scene_info_dict, {})
                    # self._recorder.flush_to_file()
                    # print(json.dumps(game.get_game_result(), indent=2))
                    attachments = game.get_game_result()['attachment']
                    print(pd.DataFrame(attachments).to_string())

                    if arg_obj.one_shot_mode or result == "QUIT":
                        break
                    game_view.reset()
                    game.reset()
        except GameProcessError as e:
            print("Error: Exception occurred in 'game' process:")
            print(e.message)
            sys.exit(errno.GAME_EXECUTION_ERROR)
    else:
        pass
        # _run_ml_mode(execution_cmd, game_config.game_setup)
    # Replace the input game_params with the parsed one
    pass
