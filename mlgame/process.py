import _winapi
import os
import signal
from multiprocessing import Process, Pipe

from .exceptions import ProcessError
from .loops import (
    GameMLModeExecutorProperty, MLExecutorProperty, TransitionExecutorPropty
)


class ProcessManager:
    """
    Create and manage processes for executing the game and the ml clients

    @var _game_proc_helper The helper object for the game process
    @var _ml_proc_helpers A list storing helper objects for all ml processes
    @var _ml_proces A list storing process objects running ml processes
    """

    def __init__(
            self, game_executor_propty: GameMLModeExecutorProperty,
            ml_executor_propties: list,
            transition_executor_propty: TransitionExecutorPropty = None):
        """
        Constructor

        @param game_executor_propty The property for the game executor
        @param ml_executor_proties A list of `MLExecutorProperty` for the ml executors
        @param transition_executor_propty The property for the transition executor
        """
        self._game_executor_propty = game_executor_propty
        self._ml_executor_propties = ml_executor_propties
        self._ml_procs = []
        self._transition_executor_propty = transition_executor_propty
        self._transition_proc = None

    def start(self):
        """
        Start the processes

        The ml processes are spawned and started first, and then the main process executes
        the game process. After returning from the game process, the ml processes will be
        terminated.

        Note that there must be 1 game process and at least 1 ml process set
        before calling this function. Otherwise, the RuntimeError will be raised.
        """
        if self._game_executor_propty is None:
            raise RuntimeError("The game process is not set. Cannot start the ProcessManager")
        if len(self._ml_executor_propties) == 0:
            raise RuntimeError("No ml process added. Cannot start the ProcessManager")

        self._create_pipes()
        self._start_ml_processes()
        self._start_transition_process()

        returncode = 0
        try:
            self._start_game_process()
        except ProcessError as e:
            # here will receive exception from ml_*P process
            print("Error: Exception occurred in '{}' process:".format(e.process_name))
            print(e.message)
            returncode = -1

        self._terminate()

        return returncode

    def _create_pipes(self):
        """
        Create communication pipes for processes
        """
        # Create pipes for Game process <-> ml process
        for ml_executor_propty in self._ml_executor_propties:
            recv_pipe_for_game, send_pipe_for_ml = Pipe(False)
            recv_pipe_for_ml, send_pipe_for_game = Pipe(False)

            self._game_executor_propty.comm_manager.add_comm_to_ml(
                ml_executor_propty.name,
                recv_pipe_for_game, send_pipe_for_game)
            ml_executor_propty.comm_manager.set_comm_to_game(
                recv_pipe_for_ml, send_pipe_for_ml)

        # Create pipe for Game process <-> Transition process
        if self._transition_executor_propty:
            recv_pipe_for_game, send_pipe_for_transition = Pipe(False)
            recv_pipe_for_transition, send_pipe_for_game = Pipe(False)

            self._game_executor_propty.comm_manager.set_comm_to_transition(
                recv_pipe_for_game, send_pipe_for_game)
            self._transition_executor_propty.comm_manager.set_comm_to_game(
                recv_pipe_for_transition, send_pipe_for_transition)

    def _start_ml_processes(self):
        """
        Spawn and start all ml processes
        """
        for propty in self._ml_executor_propties:
            process = Process(target = _ml_process_entry_point,
                              name = propty.name, args = (propty,))
            process.start()

            self._ml_procs.append(process)

    def _start_transition_process(self):
        """
        Start the transition process
        """
        if not self._transition_executor_propty:
            return

        self._transition_proc = Process(target = _transition_process_entry_point,
            name = self._transition_executor_propty.proc_name,
            args = (self._transition_executor_propty, ))
        self._transition_proc.start()

    def _start_game_process(self):
        """
        Start the game process
        """
        _game_process_entry_point(self._game_executor_propty)

    def _terminate(self):
        """
        Stop all spawned ml processes if it exists
        """
        for ml_process in self._ml_procs:
            # Send stop signal to all alive ml processes
            if ml_process.is_alive():
                self._game_executor_propty.comm_manager.send_to_ml(
                    None, ml_process.name)
                # ml_process.kill()
                if _winapi:
                    os.kill(ml_process.pid,signal.SIGINT)
                else:
                    os.kill(ml_process.pid,signal.SIGKILL)

        print("terminate")
        if self._transition_proc:
            # Send a stop signal
            self._game_executor_propty.comm_manager.send_to_transition(None)
            self._transition_proc.join()

def _game_process_entry_point(propty: GameMLModeExecutorProperty):
    """
    The real entry point of the game process
    """
    from .loops import GameMLModeExecutor

    executor = GameMLModeExecutor(propty)
    executor.start()

def _transition_process_entry_point(propty: TransitionExecutorPropty):
    """
    The entry point of the transition process
    """
    from .loops import TransitionExecutor
    executor = TransitionExecutor(propty)
    try:
        executor.start()
    except Exception as e:
        print(e)
        print("close this process: {}".format(propty.name))

def _ml_process_entry_point(propty: MLExecutorProperty):
    """
    The real entry point of the ml process
    """
    from .loops import MLExecutor

    executor = MLExecutor(propty)
    try:
        executor.start()
    # except Exception as e:
    #     exception = MLProcessError(self._name, traceback.format_exc())
    #     self._comm_manager.send_to_game(exception)
    except Exception as e:
        print(e)
        print("close this process: {}".format(propty.name))
