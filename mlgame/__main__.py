import sys
import time

from mlgame.argument.cmd_argument import parse_cmd_and_get_arg_obj
from mlgame.argument.game_argument import create_paia_game_obj
from mlgame.utils.logger import get_singleton_logger

if __name__ == '__main__':
    arg_str = " ".join(sys.argv[1:])
    logger = get_singleton_logger()
    # 1. parse command line
    arg_obj = parse_cmd_and_get_arg_obj(arg_str)

    from mlgame.core.communication import GameCommManager
    from mlgame.core.process import create_process_of_ai_clients_and_start, create_process_of_ws_and_start, terminate

    from mlgame.core.executor import GameExecutor, GameManualExecutor
    from mlgame.view.view import PygameView, DummyPygameView

    game = create_paia_game_obj(arg_obj)
    path_of_ai_clients = arg_obj.ai_clients
    ai_process = []
    ws_proc = None
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

    pass
