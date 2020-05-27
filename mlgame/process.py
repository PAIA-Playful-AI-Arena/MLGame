import importlib
import traceback

from multiprocessing import Process, Pipe
from .loops import GameMLModeExecutorProperty, MLExecutorProperty
from .exceptions import (
    GameProcessError, MLProcessError, TransitionProcessError
)

class ProcessManager:
    """
    Create and manage the processes, and set up communication channels between them

    @var _game_proc_helper The helper object for the game process
    @var _ml_proc_helpers A list storing helper objects for all ml processes
    @var _ml_proces A list storing process objects running ml processes
    """

    def __init__(self):
        self._transition_proc_helper = None
        self._transition_process = None
        self._game_executor_propty = None
        self._ml_executor_propties = []
        self._ml_procs = []

    def set_game_process(self, execution_cmd, game_cls):
        """
        Set the game process

        @param execution_cmd A `ExecutionCommand` object that contains execution config
        @param game_cls The class of the game to be executed
        """
        self._game_executor_propty = GameMLModeExecutorProperty(
            "game", execution_cmd, game_cls)

    def set_transition_process(self, transition_channel):
        """Set the transition process

        If the game runs in the online mode, set the transition process
        for sending the game progress to the remote server.

        @param transition_channel A 3-element tuple (server_ip, server_port, channel_name)
               for communicating with the remote server
        """
        self._transition_proc_helper = TransitionProcessHelper(transition_channel)

    def add_ml_process(self, name, target_module, init_args = (), init_kwargs = {}):
        """
        Add a ml process

        @param name The name of the ml process
               If it is not specified, it will be "ml_0", "ml_1", and so on.
        @param target_module The full name of the module
               to be executed in the ml process. The module must have `MLPlay` class.
        @param init_args The positional arguments to be passed to the `MLPlay.__init__()`
        @param init_kwargs The keyword arguments to be passed to the `MLPlay.__init__()`
        """
        if name == "":
            name = "ml_" + str(len(self._ml_executor_propties))

        for propty in self._ml_executor_propties:
            if name == propty.name:
                raise ValueError("The name '{}' has been used.".format(name))

        propty = MLExecutorProperty(name, target_module, init_args, init_kwargs)
        self._ml_executor_propties.append(propty)

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
        returncode = self._start_game_process()

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

            self._game_executor_propty.add_comm_to_ml(
                ml_executor_propty.name,
                recv_pipe_for_game, send_pipe_for_game)
            ml_executor_propty.set_comm_to_game(
                recv_pipe_for_ml, send_pipe_for_ml)

        # Create pipe for Game process <-> Transition process
        if self._transition_proc_helper is not None:
            recv_pipe_for_game, send_pipe_for_transition = Pipe(False)
            recv_pipe_for_transition, send_pipe_for_game = Pipe(False)

            self._game_proc_helper.set_comm_to_transition(
                recv_pipe_for_game, send_pipe_for_game)
            self._transition_proc_helper.set_comm_to_game(
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
        if self._transition_proc_helper is None:
            return

        self._transition_process = Process(target = _transition_process_entry_point,
            name = TransitionProcessHelper.name, args = (self._transition_proc_helper, ))
        self._transition_process.start()

    def _start_game_process(self):
        """
        Start the game process
        """
        if self._transition_proc_helper:
            self._game_proc_helper.to_transition = True

        returncode = 0
        try:
            _game_process_entry_point(self._game_executor_propty)
        except (MLProcessError, GameProcessError) as e:
            print("Error: Exception occurred in '{}' process:".format(e.process_name))
            print(e.message)
            returncode = 2

            # If the transition process is set, pass the exception.
            if (self._game_proc_helper.to_transition and
                isinstance(e, (MLProcessError, GameProcessError))):
                self._game_proc_helper.send_to_transition(e)

        return returncode

    def _terminate(self):
        """
        Stop all spawned ml processes if it exists
        """
        for ml_process in self._ml_procs:
            ml_process.terminate()

        if self._game_proc_helper.to_transition:
            # Send a stop signal
            self._game_proc_helper.send_to_transition(None)
            self._transition_process.join()

class TransitionProcessHelper:
    """
    The helper class for building the transition process
    """
    name = "_transition"

    def __init__(self, transition_channel):
        """
        Constructor

        @param transition_channel A 3-element tuple (server_ip, server_port, channel_name)
        """
        self.transition_channel = transition_channel
        self._comm_to_game = CommunicationHandler()

    def set_comm_to_game(self, recv_end, send_end):
        """
        Set communication objects for communicating with game process

        @param recv_end The communication object for receiving objects from game process
        @param send_end the communication object for sending objects to game process
        """
        self._comm_to_game.set_recv_end(recv_end)
        self._comm_to_game.set_send_end(send_end)

    def recv_from_game(self):
        """
        Receive the object sent from the game process
        """
        return self._comm_to_game.recv()

    def send_exception(self, exception: TransitionProcessError):
        """
        Send an exception to the game process
        """
        self._comm_to_game.send(exception)

def _game_process_entry_point(propty: GameMLModeExecutorProperty):
    """
    The real entry point of the game process
    """
    from .loops import GameMLModeExecutor

    executor = GameMLModeExecutor(propty)
    executor.start()

def _transition_process_entry_point(helper: TransitionProcessHelper):
    """
    The entry point of the transition process
    """
    try:
        from .transition import TransitionManager
        transition_manager = TransitionManager(
            helper.recv_from_game, helper.transition_channel)
        transition_manager.transition_loop()
    except Exception as e:
        exception = TransitionProcessError(helper.name, traceback.format_exc())
        helper.send_exception(exception)

def _ml_process_entry_point(propty: MLExecutorProperty):
    """
    The real entry point of the ml process
    """
    from .loops import MLExecutor

    executor = MLExecutor(propty)
    executor.start()
