import time
from multiprocessing import Process, Pipe

from mlgame.core.env import TIMEOUT
from mlgame.core.executor import AIClientExecutor, WebSocketExecutor, ProgressLogExecutor
from mlgame.core.communication import GameCommManager, MLCommManager, TransitionCommManager
from mlgame.utils.enum import get_ai_name
from mlgame.utils.logger import logger
from mlgame.game.paia_game import PaiaGame


def create_process_of_ws_and_start(game_comm: GameCommManager, ws_url) -> Process:
    recv_pipe_for_game, send_pipe_for_ws = Pipe(False)
    recv_pipe_for_ws, send_pipe_for_game = Pipe(False)
    ws_comm = TransitionCommManager(recv_pipe_for_ws, send_pipe_for_ws)
    game_comm.add_comm_to_others("ws", recv_pipe_for_game, send_pipe_for_game)
    ws_executor = WebSocketExecutor(ws_uri=ws_url, ws_comm=ws_comm)
    process = Process(target=ws_executor.run, name="ws")
    # process = ws_executor
    process.start()
    # time.sleep(0.1)
    return process


def create_process_of_ai_clients_and_start(
        game_comm: GameCommManager, path_of_ai_clients: list,game_params:dict) -> list:
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
        ai_executor = AIClientExecutor(ai_client.__str__(), ai_comm, ai_name=ai_name,game_params=game_params)
        process = Process(target=ai_executor.run,
                          name=ai_name)
        process.start()
        ai_process.append(process)
    return ai_process

def create_process_of_progress_log_and_start(game_comm: GameCommManager, progress_folder, progress_frame_frequency) -> Process:
    recv_pipe_for_game, send_pipe_for_pl = Pipe(False)
    recv_pipe_for_pl, send_pipe_for_game = Pipe(False)
    pl_comm = TransitionCommManager(recv_pipe_for_pl, send_pipe_for_pl)
    game_comm.add_comm_to_others("pl", recv_pipe_for_game, send_pipe_for_game)
    pl_executor = ProgressLogExecutor(progress_folder=progress_folder, progress_frame_frequency=progress_frame_frequency, pl_comm=pl_comm)
    process = Process(target=pl_executor.run, name="pl")
    process.start()
    # time.sleep(0.1)
    return process


def terminate(game_comm: GameCommManager, ai_process: list, ws_proc: Process, progress_proc: Process):
    logger.info("Main process will terminate ai process")
    # 5.terminate
    for ai_proc in ai_process:
        # Send stop signal to all alive ml processes
        if ai_proc.is_alive():
            game_comm.send_to_ml(
                None, ai_proc.name)
            ai_proc.terminate()
    logger.info("Main process will terminate ws process")

    if ws_proc is not None:
        timeout = time.time() + TIMEOUT
        print(f"wait to close ws for timeout : {TIMEOUT} s")
        while True:
            time.sleep(0.2)
            if time.time() > timeout:
                ws_proc.terminate()
                ws_proc.join()
                break
            elif not ws_proc.is_alive():
                break
        logger.info(f"use {time.time() - timeout + TIMEOUT} to close.")
    
    if progress_proc is not None:
        timeout = time.time() + TIMEOUT
        print(f"wait to close progress for timeout : {TIMEOUT} s")
        while True:
            time.sleep(0.2)
            if time.time() > timeout:
                progress_proc.terminate()
                progress_proc.join()
                break
            elif not progress_proc.is_alive():
                break
        logger.info(f"use {time.time() - timeout + TIMEOUT} to close.")
    logger.info("Game is terminated")
