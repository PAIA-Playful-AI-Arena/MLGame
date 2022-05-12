import time
from multiprocessing import Process, Pipe

from mlgame.core.executor import AIClientExecutor, WebSocketExecutor
from mlgame.core.communication import GameCommManager, MLCommManager, TransitionCommManager
from mlgame.utils.enum import get_ai_name
from mlgame.utils.logger import logger


def create_process_of_ws_and_start(game_comm: GameCommManager, ws_url):
    recv_pipe_for_game, send_pipe_for_ws = Pipe(False)
    recv_pipe_for_ws, send_pipe_for_game = Pipe(False)
    ws_comm = TransitionCommManager(recv_pipe_for_ws, send_pipe_for_ws)
    game_comm.add_comm_to_others("ws", recv_pipe_for_game, send_pipe_for_game)
    ws_executor = WebSocketExecutor(ws_uri=ws_url, ws_comm=ws_comm)
    process = Process(target=ws_executor.run, name="ws")
    process.start()
    time.sleep(0.1)
    return process


def create_process_of_ai_clients_and_start(
        game_comm: GameCommManager, path_of_ai_clients: list) -> list:
    """
    return a process list to main process and bind pipes to `game_comm`
    """
    ai_process = []
    for index, ai_client in enumerate(path_of_ai_clients):
        ai_name = get_ai_name(index)
        recv_pipe_for_game, send_pipe_for_ml = Pipe(False)
        recv_pipe_for_ml, send_pipe_for_game = Pipe(False)
        game_comm.add_comm_to_ml(
            ai_name,
            recv_pipe_for_game, send_pipe_for_game)
        ai_comm = MLCommManager(ai_name)
        ai_comm.set_comm_to_game(
            recv_pipe_for_ml, send_pipe_for_ml)
        ai_executor = AIClientExecutor(ai_client.__str__(), ai_comm, ai_name=ai_name)
        process = Process(target=ai_executor.run,
                          name=ai_name)
        process.start()
        ai_process.append(process)
    return ai_process


def terminate(game_comm: GameCommManager, ai_process, ws_proc):
    logger.info("Game is going to terminate")
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
    logger.info("Game is terminated")
