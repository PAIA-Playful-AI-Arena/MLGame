import sys

import pydantic

from mlgame.communication import GameCommManager
from mlgame.exceptions import GameConfigError
from mlgame.gameconfig import GameConfig
from mlgame.process import create_process_of_ai_clients_and_start
from mlgame.argument import get_parser_from_dict
from mlgame.utils.logger import get_singleton_logger
from mlgame.argument import create_MLGameArgument_obj
from mlgame.executor import GameExecutor, GameManualExecutor

if __name__ == '__main__':
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
        _logger.error(f"Error in parsing game parameter : {e.__str__()}")
        # _logger.info("game is exited")
        sys.exit()

    # 3. get parsed_game_params
    # Program will catch parse error (error in game parameter in cli) here.
    param_parser = get_parser_from_dict(game_config.game_params)
    parsed_game_params = param_parser.parse_args(arg_obj.game_params)
    # if parse config error game will exit at system code 2

    game_setup = game_config.game_setup
    game_cls = game_setup["game"]
    entity_of_ai_clients = game_setup["ml_clients"]
    path_of_ai_clients = arg_obj.ai_clients

    # 4. prepare ai_clients , create pipe, start ai_client process
    if arg_obj.is_manual:
        ai_process = []
        game_comm = None
        # TODO create executor class
        game_executor = GameManualExecutor(
            game_cls, parsed_game_params.__dict__,
            fps=arg_obj.fps, one_shot_mode=arg_obj.one_shot_mode)
    else:
        game_comm = GameCommManager()
        ai_process = create_process_of_ai_clients_and_start(
            game_comm=game_comm, ai_entity_defined_by_game=entity_of_ai_clients,
            path_of_ai_clients=path_of_ai_clients)

        # 5. run game in main process
        game_executor = GameExecutor(
            game_cls, parsed_game_params.__dict__, game_comm,
            fps=arg_obj.fps, one_shot_mode=arg_obj.one_shot_mode)
    try:
        game_executor.run()
    except Exception as e:
        # handle unknown exception
        _logger.exception("Some errors happened in game process.")
        # print(traceback.format_exc())
        # print(e.__str__())
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
        print("Game is terminated")

    pass
