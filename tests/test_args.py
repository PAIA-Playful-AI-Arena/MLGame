import importlib
import inspect
import os
import random
import sys
import time

import pandas as pd
import pydantic

from mlgame.core import errno
from mlgame.core.exceptions import GameProcessError
from mlgame.argument.model import GameConfig
from mlgame.gamedev.game_interface import PaiaGame
from mlgame.gamedev.generic import quit_or_esc
from mlgame.argument.argument import create_game_arg_parser, create_cli_args_parser
from mlgame.view.view import PygameView
from mlgame.argument.argument import parse_cmd_and_get_arg_obj
from tests.mock_included_file import MockMLPlay


def get_parsed_args_or_print_help(arg_str):
    arg_parser = create_cli_args_parser()
    parsed_args = arg_parser.parse_args(arg_str.split())
    if parsed_args.help:
        arg_parser.print_help()
        sys.exit()
    return parsed_args


def test_to_get_fps_and_one_shot_mode():
    fps = random.randint(10, 100)
    arg_str = f"-f {fps} " \
              " mygame --user 1 --map 2"

    parsed_args = get_parsed_args_or_print_help(arg_str)
    assert parsed_args.fps == fps
    assert not parsed_args.one_shot_mode

    arg_str = f"-1 " \
              " mygame --user 1 --map 2"
    parsed_args = get_parsed_args_or_print_help(arg_str)
    assert parsed_args.fps == 30
    assert parsed_args.one_shot_mode
    assert parsed_args.ai_clients is None
    # parse args to get file and import module class


def test_to_get_ai_module():
    arg_str = "-i ./mock_included_file.py -i ../tests/mock_included_file.py " \
              "--input-ai /Users/kylin/Documents/02-PAIA_Project/MLGame/tests/mock_included_file.py" \
              " mygame --user 1 --map 2"
    parsed_args = get_parsed_args_or_print_help(arg_str)
    assert parsed_args.ai_clients
    # parse args to get file and import module class
    for file in parsed_args.ai_clients:
        assert_contain_MockMLPlay(file)


def assert_contain_MockMLPlay(file):
    module_name = os.path.basename(file)
    module_name = module_name.replace('.py', '')
    spec = importlib.util.spec_from_file_location(module_name, file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert inspect.ismodule(module)
    assert inspect.getmembers(module, inspect.isclass)
    assert inspect.isclass(module.MockMLPlay)
    obj1 = module.MockMLPlay()
    obj2 = MockMLPlay()
    assert type(obj1).__name__ == type(obj2).__name__
    assert obj2.func() == obj1.func()


def test_use_argument_model():
    arg_str = "-f 60 -1 -i ./mock_included_file.py -i ../tests/mock_included_file.py " \
              "--input-ai /Users/kylin/Documents/02-PAIA_Project/MLGame/tests/mock_included_file.py" \
              " ../games/easy_gam --score 10 --color FF9800 --time_to_play 600 --total_point 50"
    try:
        arg_obj = parse_cmd_and_get_arg_obj(arg_str)
        assert False
    except pydantic.ValidationError as e:
        print(e.__str__())
    arg_str = "-f 60 -1 -i ./mock_included_file.py -i ../tests/mock_included_file.py " \
              "--input-ai /Users/kylin/Documents/02-PAIA_Project/MLGame/tests/mock_included_file.py" \
              " ../games/easy_game --score 10 --color FF9800 --time_to_play 600 --total_point 50"
    arg_obj = parse_cmd_and_get_arg_obj(arg_str)
    assert arg_obj.one_shot_mode is True
    assert arg_obj.is_manual is False
    for file in arg_obj.ai_clients:
        assert_contain_MockMLPlay(file)


def test_play_easy_game_in_manual_mode():
    arg_str = "-f 60 -1 " \
              "../games/easy_game --score 10 --color FF9800 --time_to_play 600 --total_point 50"
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


from multiprocessing import Process


class MLExecutor:
    """
    The loop executor for the machine learning process
    """

    def __init__(self, ai_client: str, comm, *args, **kwargs):
        # self._target_module = propty.target_module
        self.ai_client = ai_client
        self._init_args = args
        self._init_kwargs = kwargs
        self._comm_manager = comm
        # self._frame_count = 0

    def start(self):
        """
        Start the loop for the machine learning process
        """
        self._comm_manager.start_recv_obj_thread()

        try:
            module_name = os.path.basename(self.ai_client)
            spec = importlib.util.spec_from_file_location(module_name, self.ai_client)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            ml_module = module
            ml = ml_module.MLPlay(*self._init_args, **self._init_kwargs)

            self._ml_ready()
            while True:
                scene_info, keyboard_info = self._comm_manager.recv_from_game()
                if scene_info is None:
                    # game over
                    break
                # assert keyboard_info == "1"
                command = ml.update(scene_info, keyboard_info)
                if scene_info["status"] != "GAME_ALIVE" or command == "RESET":
                    command = "RESET"
                    ml.reset()
                    self._frame_count = 0
                    self._ml_ready()
                    continue

                if command is not None:
                    self._comm_manager.send_to_game({
                        "frame": self._frame_count,
                        "command": command
                    })

                self._frame_count += 1

        except Exception:
            # exception = MLProcessError(self._name,
            #                            "The process '{}' is exited by itself. {}"
            #                            .format(self._name, traceback.format_exc()))
            # self._comm_manager.send_to_game(exception)
            sys.exit()

    def _ml_ready(self):
        """
        Send a "READY" command to the game process
        """
        self._comm_manager.send_to_game("READY")


def _ml_process_entry_point(ai_client: str):
    # MLCommManager()
    executor = MLExecutor(ai_client=ai_client, comm="")
    pass


def start_ml_process(ai_clients: []):
    for index, ai_client in enumerate(ai_clients, 1):
        process = Process(target=_ml_process_entry_point,
                          name=f"ai_client_{index}", args=(ai_client,))
        process.start()
