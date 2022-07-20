import datetime
import sys
import time

from mlgame.argument.cmd_argument import parse_cmd_and_get_arg_obj
from mlgame.argument.tool import revise_ai_clients
from mlgame.game.paia_game import get_paia_game_obj
from mlgame.utils.logger import logger

if __name__ == '__main__':
    import os
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

    # 1. parse command line
    arg_obj = parse_cmd_and_get_arg_obj(sys.argv[1:])

    # 2. get parsed_game_params
    from mlgame.argument.game_argument import GameConfig
    game_config = GameConfig(arg_obj.game_folder.__str__())
    parsed_game_params = game_config.parse_game_params(arg_obj.game_params)
    path_of_ai_clients = revise_ai_clients(arg_obj.ai_clients, game_config.user_num_config)
    user_num = len(path_of_ai_clients)
    game = get_paia_game_obj(game_config.game_cls, parsed_game_params, user_num)

    ai_process = []
    ws_proc = None

    print(f"===========Game is started at {datetime.datetime.now()}===========")
    from mlgame.core.communication import GameCommManager
    from mlgame.core.process import create_process_of_ai_clients_and_start, create_process_of_ws_and_start, terminate
    from mlgame.core.executor import GameExecutor, GameManualExecutor
    from mlgame.view.view import PygameView, DummyPygameView
    game_comm = GameCommManager()
    try:
        if arg_obj.ws_url:
            # prepare transmitter for game executor
            ws_proc = create_process_of_ws_and_start(game_comm, arg_obj.ws_url)

        # 4. prepare ai_clients , create pipe, start ai_client process
        if arg_obj.is_manual:
            # only play in local and manual mode and will show view
            # TODO to deprecated and use ml_play_manual.py to alternate
            game_view = PygameView(game.get_scene_init_data())
            game_executor = GameManualExecutor(
                game, game_view, game_comm, fps=arg_obj.fps, one_shot_mode=arg_obj.one_shot_mode)

        else:
            # play game with ai_clients
            if arg_obj.no_display:
                game_view = DummyPygameView(game.get_scene_init_data())
            else:
                game_view = PygameView(game.get_scene_init_data())
            ai_process = create_process_of_ai_clients_and_start(
                game_comm=game_comm,
                path_of_ai_clients=path_of_ai_clients)
            # 5. run game in main process
            game_executor = GameExecutor(
                game, game_comm, game_view,
                fps=arg_obj.fps, one_shot_mode=arg_obj.one_shot_mode, no_display=arg_obj.no_display)
        time.sleep(0.1)
        game_executor.run()

    except Exception as e:
        # finally
        logger.exception(f"Exception in {__file__} : {e.__str__()}")
        pass
    finally:
        terminate(game_comm, ai_process, ws_proc)
    print(f"===========All process is terminated at {datetime.datetime.now()}===========")
    pass
