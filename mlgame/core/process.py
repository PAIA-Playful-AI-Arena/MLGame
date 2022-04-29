import time
from multiprocessing import Process, Pipe

from mlgame.argument.model import AI_NAMES
from mlgame.core.executor import AIClientExecutor, WebSocketExecutor
from mlgame.core.communication import GameCommManager, MLCommManager, TransitionCommManager
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
        ai_name = AI_NAMES[index]
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

#
# class ProcessManager:
#     """
#     Create and manage processes for executing the game and the ml clients
#
#     @var _game_proc_helper The helper object for the game process
#     @var _ml_proc_helpers A list storing helper objects for all ml processes
#     @var _ml_proces A list storing process objects running ml processes
#     """
#
#     def __init__(
#             self, game_executor_propty: GameMLModeExecutorProperty,
#             ml_executor_propties: list):
#         """
#         Constructor
#
#         @param game_executor_propty The property for the game executor
#         @param ml_executor_proties A list of `MLExecutorProperty` for the ml executors
#         """
#         self._game_executor_propty = game_executor_propty
#         self._ml_executor_propties = ml_executor_propties
#         self._ml_procs = []
#
#     def start(self):
#         """
#         Start the processes
#
#         The ml processes are spawned and started first, and then the main process executes
#         the game process. After returning from the game process, the ml processes will be
#         terminated.
#
#         Note that there must be 1 game process and at least 1 ml process set
#         before calling this function. Otherwise, the RuntimeError will be raised.
#         """
#         if self._game_executor_propty is None:
#             raise RuntimeError("The game process is not set. Cannot start the ProcessManager")
#         if len(self._ml_executor_propties) == 0:
#             raise RuntimeError("No ml process added. Cannot start the ProcessManager")
#
#         self._create_pipes()
#         self._start_ml_processes()
#
#         returncode = 0
#         try:
#             self._start_game_process()
#         except ProcessError as e:
#             # here will receive exception from ml_*P process
#             print("Error: Exception occurred in '{}' process:".format(e.process_name))
#             print(e.message)
#             returncode = -1
#
#         self._terminate()
#
#         return returncode
#
#     def _create_pipes(self):
#         """
#         Create communication pipes for processes
#         """
#         # Create pipes for Game process <-> ml process
#         for ml_executor_propty in self._ml_executor_propties:
#             recv_pipe_for_game, send_pipe_for_ml = Pipe(False)
#             recv_pipe_for_ml, send_pipe_for_game = Pipe(False)
#
#             self._game_executor_propty.comm_manager.add_comm_to_ml(
#                 ml_executor_propty.name,
#                 recv_pipe_for_game, send_pipe_for_game)
#             ml_executor_propty.comm_manager.set_comm_to_game(
#                 recv_pipe_for_ml, send_pipe_for_ml)
#
#     def _start_ml_processes(self):
#         """
#         Spawn and start all ml processes
#         """
#         for propty in self._ml_executor_propties:
#             process = Process(target = _ml_process_entry_point,
#                               name = propty.name, args = (propty,))
#             process.start()
#
#             self._ml_procs.append(process)
#
#     def _start_game_process(self):
#         """
#         Start the game process
#         """
#         _game_process_entry_point(self._game_executor_propty)
#
#     def _terminate(self):
#         """
#         Stop all spawned ml processes if it exists
#         """
#         for ml_process in self._ml_procs:
#             # Send stop signal to all alive ml processes
#             if ml_process.is_alive():
#                 self._game_executor_propty.comm_manager.send_to_ml(
#                     None, ml_process.name)
#                 ml_process.terminate()
