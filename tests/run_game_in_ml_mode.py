from multiprocessing import Process, Pipe

from mlgame.core.communication import GameCommManager, MLCommManager
from mlgame.argument.model import GameConfig
from mlgame.argument.argument import create_game_arg_parser
from mlgame.argument.argument import parse_cmd_and_get_arg_obj
from mlgame.core.executor import GameExecutor, AIClientExecutor

if __name__ == '__main__':
    arg_str = "-f 120  -i /Users/kylin/Documents/02-PAIA_Project/MLGame/games/easy_game/ml/ml_play_template.py " \
              "/Users/kylin/Documents/02-PAIA_Project/MLGame/games/easy_game " \
              "--score 10 --color FF9800 --time_to_play 600 --total_point 50"
    # 1. parse command line
    arg_obj = parse_cmd_and_get_arg_obj(arg_str)

    # 2. parse game_folder/config.py and get game_config
    game_config = GameConfig(arg_obj.game_folder.__str__())
    assert game_config
    param_parser = create_game_arg_parser(game_config.game_params)
    # 3. get parsed_game_params
    parsed_game_params = param_parser.parse_args(arg_obj.game_params)
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

        ai_executor = AIClientExecutor(ai_client.__str__(), ai_comm, args, kwargs)
        process = Process(target=ai_executor.run,
                          name=ml_name)
        process.start()
        ai_process.append(process)

    # 5. run game in main process
    game_executor = GameExecutor(game_cls, parsed_game_params.__dict__, game_comm,
                                 fps=arg_obj.fps, one_shot_mode=arg_obj.one_shot_mode)
    game_executor.run()

    # 5.terminate
    for ai_proc in ai_process:
        # Send stop signal to all alive ml processes
        if ai_proc.is_alive():
            game_comm.send_to_ml(
                None, ai_proc.name)
            ai_proc.terminate()
