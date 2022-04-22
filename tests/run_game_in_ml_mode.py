from multiprocessing import Process, Pipe

from mlgame.communication import GameCommManager, MLCommManager
from mlgame.gameconfig import GameConfig
from mlgame.utils.argparser_generator import get_parser_from_dict
from tests.argument import create_MLGameArgument_obj
from tests.executor import GameExecutor, AIClientExecutor

if __name__ == '__main__':
    arg_str = "-f 60 -1 -i /Users/kylin/Documents/02-PAIA_Project/MLGame/games/easy_game/ml/ml_play_template.py " \
              "/Users/kylin/Documents/02-PAIA_Project/MLGame/games/easy_game " \
              "--score 10 --color FF9800 --time_to_play 600 --total_point 50"
    arg_obj = create_MLGameArgument_obj(arg_str)
    # parse game_folder/config.py
    game_config = GameConfig(arg_obj.game_folder.__str__())
    assert game_config
    param_parser = get_parser_from_dict(game_config.game_params)
    parsed_game_params = param_parser.parse_args(arg_obj.game_params)

    game_setup = game_config.game_setup
    game_cls = game_setup["game"]
    _frame_interval = 1 / arg_obj.fps

    # prepare ai_clients
    """
    Spawn and start all ml processes
    """
    # create pipe
    pipe_of_game_to_ai = []
    pipe_of_ai_to_game = []
    game_comm = GameCommManager()
    ai_process = []
    for index, ai_client in enumerate(arg_obj.ai_clients, 1):
        ai_name = f"ai_client_{index}"
        recv_pipe_for_game, send_pipe_for_ml = Pipe(False)
        recv_pipe_for_ml, send_pipe_for_game = Pipe(False)
        game_comm.add_comm_to_ml(
            ai_name,
            recv_pipe_for_game, send_pipe_for_game)

        ai_comm = MLCommManager(ai_name)
        ai_comm.set_comm_to_game(
            recv_pipe_for_ml, send_pipe_for_ml)

        ai_executor = AIClientExecutor(ai_comm)
        process = Process(target=ai_executor.run,
                          name=ai_name)
        process.start()
        ai_process.append(process)

    game_executor = GameExecutor(game_comm)
    game_executor.run()
    # terminate

    for ai_proc in ai_process:
        # Send stop signal to all alive ml processes
        if ai_proc.is_alive():
            game_comm.send_to_ml(
                None, ai_proc.name)
            ai_proc.terminate()
