import sys
import traceback
from multiprocessing import Process, Pipe

import pydantic

from mlgame.communication import GameCommManager, MLCommManager
from mlgame.gameconfig import GameConfig
from mlgame.utils.argparser_generator import get_parser_from_dict
from tests.argument import create_MLGameArgument_obj
from tests.executor import AIClientExecutor, GameExecutor

if __name__ == '__main__':
    arg_str = " ".join(sys.argv[1:])
    # 1. parse command line
    try:
        arg_obj = create_MLGameArgument_obj(arg_str)
        # TODO  add help
    except pydantic.ValidationError as e:
        # TODO should we return to server ?
        print(e.__str__())
        sys.exit()

    # 2. parse game_folder/config.py and get game_config
    game_config = GameConfig(arg_obj.game_folder.__str__())
    # TODO catch GameConfigError (error in game)

    param_parser = get_parser_from_dict(game_config.game_params)
    # 3. get parsed_game_params
    # TODO catch parse error (error in game parameter in cli)
    parsed_game_params = param_parser.parse_args(arg_obj.game_params)
    # if parse config error game will exit at system code 2

    game_setup = game_config.game_setup
    game_cls = game_setup["game"]

    pipe_of_game_to_ai = []
    pipe_of_ai_to_game = []
    game_comm = GameCommManager()
    ai_process = []
    # 4. prepare ai_clients , create pipe, start ai_client process
    for index, ai_client in enumerate(arg_obj.ai_clients):
        ai_client_info_defined_by_game = game_setup["ml_clients"][index]
        ml_name = ai_client_info_defined_by_game["name"]
        args = ai_client_info_defined_by_game.get("args", ())
        kwargs = ai_client_info_defined_by_game.get("kwargs", {})

        recv_pipe_for_game, send_pipe_for_ml = Pipe(False)
        recv_pipe_for_ml, send_pipe_for_game = Pipe(False)
        game_comm.add_comm_to_ml(
            ml_name,
            recv_pipe_for_game, send_pipe_for_game)

        ai_comm = MLCommManager(ml_name)
        ai_comm.set_comm_to_game(
            recv_pipe_for_ml, send_pipe_for_ml)
        # TODO catch ai_client error
        ai_executor = AIClientExecutor(ai_client.__str__(), ai_comm, args, kwargs)
        process = Process(target=ai_executor.run,
                          name=ml_name)
        process.start()
        ai_process.append(process)

    # 5. run game in main process
    game_executor = GameExecutor(game_cls, parsed_game_params.__dict__, game_comm,
                                 fps=arg_obj.fps, one_shot_mode=arg_obj.one_shot_mode)
    try:
        game_executor.run()
    except Exception as e:
        # TODO handle game error
        # print(traceback.format_exc())
        print(e.__str__())
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