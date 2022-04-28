import sys
import time
from multiprocessing import Pipe, Process

import pydantic

from mlgame.utils.communication import GameCommManager, TransitionCommManager
from mlgame.core.exceptions import GameConfigError
from mlgame.argument.model import GameConfig
from mlgame.gamedev.game_interface import PaiaGame
from mlgame.core.process import create_process_of_ai_clients_and_start
from mlgame.argument.argument import create_game_arg_parser
from mlgame.utils.logger import get_singleton_logger
from mlgame.argument.argument import create_MLGameArgument_obj
from mlgame.core.executor import GameExecutor, GameManualExecutor, WebSocketExecutor
from mlgame.view.view import PygameView, DummyPygameView


def get_paia_game_obj(game_cls, parsed_game_params: dict) -> PaiaGame:
    game = game_cls(**parsed_game_params)
    assert isinstance(game, PaiaGame), "Game " + str(game) + " should implement a abstract class : PaiaGame"
    return game


if __name__ == '__main__':
    # try:
    #     subcommand = self.argv[1]
    # except IndexError:
    #     subcommand = "help"  # Display help if no arguments were given.
    arg_str = " ".join(sys.argv[1:])
    _logger = get_singleton_logger()
    # 1. parse command line
    try:
        arg_obj = create_MLGameArgument_obj(arg_str)
        # 2. parse game_folder/config.py and get game_config
        game_config = GameConfig(arg_obj.game_folder.__str__())
    except pydantic.ValidationError as e:
        _logger.error(f"Error in parsing command : {e.__str__()}")

        sys.exit()
    except GameConfigError as e:
        _logger.exception(f"Error in parsing game parameter : {e.__str__()}")
        # _logger.info("game is exited")
        sys.exit()

    # 3. get parsed_game_params
    # Program will catch parse error (error in game parameter in cli) here.
    param_parser = create_game_arg_parser(game_config.game_params)
    parsed_game_params = param_parser.parse_args(arg_obj.game_params)
    # if parse config error game will exit at system code 2

    game_setup = game_config.game_setup
    game_cls = game_setup["game"]
    game = get_paia_game_obj(game_cls, parsed_game_params.__dict__)
    entity_of_ai_clients = game_setup["ml_clients"]
    path_of_ai_clients = arg_obj.ai_clients
    ws_proc = None

    # 4. prepare ai_clients , create pipe, start ai_client process
    if arg_obj.is_manual:
        # play in local and manual mode
        ai_process = []
        game_comm = None
        game_view = PygameView(game.get_scene_init_data())

        game_executor = GameManualExecutor(
            game, game_view, fps=arg_obj.fps, one_shot_mode=arg_obj.one_shot_mode)

    else:
        # play in local and ai mode
        game_comm = GameCommManager()
        ai_process = create_process_of_ai_clients_and_start(
            game_comm=game_comm, ai_entity_defined_by_game=entity_of_ai_clients,
            path_of_ai_clients=path_of_ai_clients)
        if arg_obj.ws_url:
            _logger.debug(arg_obj.ws_url)
            # prepare transmitter for game executor
            recv_pipe_for_game, send_pipe_for_ws = Pipe(False)
            recv_pipe_for_ws, send_pipe_for_game = Pipe(False)
            ws_comm = TransitionCommManager(recv_pipe_for_ws, send_pipe_for_ws)
            game_comm.add_comm_to_others("ws", recv_pipe_for_game, send_pipe_for_game)
            ws_executor = WebSocketExecutor(ws_uri=arg_obj.ws_url, ws_comm=ws_comm)
            process = Process(target=ws_executor.run, name="ws")
            process.start()
            ws_proc = process
            pass
        else:
            pass
        # ws will start another process to
        if arg_obj.no_display:
            game_view = DummyPygameView(game.get_scene_init_data())
        else:
            game_view = PygameView(game.get_scene_init_data())

        # 5. run game in main process
        game_executor = GameExecutor(
            game, game_comm, game_view,
            fps=arg_obj.fps, one_shot_mode=arg_obj.one_shot_mode, no_display=arg_obj.no_display)
    try:
        game_executor.run()
    except Exception as e:
        # send to es
        _logger.exception("Some errors happened in game process.")

        pass
    finally:
        print("Game is going to terminate")
        # 5.terminate
        for ai_proc in ai_process:
            # Send stop signal to all alive ml processes
            if ai_proc.is_alive():
                game_comm.send_to_ml(
                    None, ai_proc.name)
                ai_proc.terminate()
        if ws_proc is not None:
            time.sleep(0.1)
            if ws_proc.is_alive():
                game_comm.send_to_others(None)
                ws_proc.terminate()
        print("Game is terminated")

    pass
