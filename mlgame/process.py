import importlib
import traceback

from multiprocessing import Process, Pipe
from .communication.base import CommunicationSet, CommunicationHandler
from .exception import (
    GameProcessError, MLProcessError, TransitionProcessError, \
        trim_callstack
)

class ProcessManager:
    """
    Create and manage the processes, and set up communication channels between them

    @var _game_proc_helper The helper object for the game process
    @var _ml_proc_helpers A list storing helper objects for all ml processes
    @var _ml_proces A list storing process objects running ml processes
    """

    def __init__(self):
        self._game_proc_helper = None
        self._transition_proc_helper = None
        self._transition_process = None
        self._ml_proc_helpers = []
        self._ml_procs = []

    def set_game_process(self, target, args = (), kwargs = {}):
        """
        Set the game process

        @param target A target function which is the starting point of the game process
        @param args The positional arguments to be passed to the target function
        @param kwargs The keyword arguments to be passed to the target function
        """
        self._game_proc_helper = GameProcessHelper(target, args, kwargs)

    def set_transition_process(self, server_ip, server_port, channel_name):
        """Set the transition process

        If the game runs in the online mode, set the transition process
        for sending the game progress to the remote server.

        @param server_ip The IP of the remote server
        @param server_port The port of the remote server
        @param channel_name The name of the communication channel in the remote server
        """
        self._transition_proc_helper = TransitionProcessHelper(server_ip, server_port, channel_name)

    def add_ml_process(self, target_module, name = "", args = (), kwargs = {}):
        """
        Add a ml process

        @param target_module The full name of the module
               to be executed in the ml process. The module must have `ml_loop` function.
        @param name The name of the ml process
               If it is not specified, it will be "ml_0", "ml_1", and so on.
        @param args The positional arguments to be passed to the `ml_loop` function
        @param kwargs The keyword arguments to be passed to the `ml_loop` function
        """
        if name == "":
            name = "ml_" + str(len(self._ml_proc_helpers))

        for helper in self._ml_proc_helpers:
            if name == helper.name:
                raise ValueError("The name '{}' has been used.".format(name))

        helper = MLProcessHelper(target_module, name, args, kwargs)
        self._ml_proc_helpers.append(helper)

    def start(self):
        """
        Start the processes

        The ml processes are spawned and started first, and then the main process executes
        the game process. After returning from the game process, the ml processes will be
        terminated.

        Note that there must be 1 game process and at least 1 ml process set
        before calling this function. Otherwise, the RuntimeError will be raised.
        """
        if self._game_proc_helper is None:
            raise RuntimeError("The game process is not set. Cannot start the ProcessManager")
        if len(self._ml_proc_helpers) == 0:
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
        for ml_proc_helper in self._ml_proc_helpers:
            recv_pipe_for_game, send_pipe_for_ml = Pipe(False)
            recv_pipe_for_ml, send_pipe_for_game = Pipe(False)

            self._game_proc_helper.add_comm_to_ml(ml_proc_helper.name,
                recv_pipe_for_game, send_pipe_for_game)
            ml_proc_helper.set_comm_to_game(
                recv_pipe_for_ml, send_pipe_for_ml)

        # Create pipe for Game process <-> Transition process
        if self._transition_proc_helper is not None:
            recv_pipe_for_game, send_pipe_for_transition = Pipe(False)
            recv_pipe_for_transition, send_pipe_for_game = Pipe(False)

            self._game_proc_helper.set_comm_to_transition( \
                recv_pipe_for_game, send_pipe_for_game)
            self._transition_proc_helper.set_comm_to_game( \
                recv_pipe_for_transition, send_pipe_for_transition)

    def _start_ml_processes(self):
        """
        Spawn and start all ml processes
        """
        for ml_proc_helper in self._ml_proc_helpers:
            process = Process(target = _ml_process_entry_point,
                name = ml_proc_helper.name, args = (ml_proc_helper,))
            process.start()

            self._ml_procs.append(process)

    def _start_transition_process(self):
        """Start the transition process
        """
        if self._transition_proc_helper is None:
            return

        self._transition_process = Process(target = _transition_process_entry_point, \
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
            _game_process_entry_point(self._game_proc_helper)
        except (MLProcessError, GameProcessError) as e:
            print("*** Error occurred in '{}' process:".format(e.process_name))
            print(e.message)
            returncode = 2

            # If the transition process is set, pass the exception.
            if self._game_proc_helper.to_transition and \
                isinstance(e, (MLProcessError, GameProcessError)):
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


class GameProcessHelper:
    """
    The helper class that helps build the game process

    Store the information for starting the game process and
    provide the helper functions to communicate with the ml processes.
    """
    name = "_game"

    def __init__(self, target_function, args = (), kwargs = {}):
        """
        Constructor

        @param target_function The starting point of the game process
        @param args The positional arguments to be passed to the target function
        @param kwargs The keyword arguments to be passed to the target function
        """
        self.target_function = target_function
        self.args = args
        self.kwargs = kwargs
        self._comm_to_ml_set = CommunicationSet()
        self.to_transition = False
        self._comm_to_transition = CommunicationHandler()

    def add_comm_to_ml(self, to_ml: str, recv_end, send_end):
        """
        Add communication objects for communicating with specified ml process

        @param to_ml The name of the target ml process
        @param recv_end The communication object for receiving objects from that ml process
        @param send_end The communication object for sending objects to that ml process
        """
        self._comm_to_ml_set.add_recv_end(to_ml, recv_end)
        self._comm_to_ml_set.add_send_end(to_ml, send_end)

    def send_to_ml(self, obj, to_ml: str):
        """
        Send an object to the specified ml process

        @param obj The object to be sent
        @param to_ml The name of the ml process
        """
        self._comm_to_ml_set.send(obj, to_ml)

    def send_to_all_ml(self, obj):
        """
        Send an object to all ml processes

        @param obj The object to be sent
        """
        self._comm_to_ml_set.send_all(obj)

    def recv_from_ml(self, from_ml: str, to_wait: bool = False):
        """
        Receive an object from the specified ml process

        If it receives an exception from the ml process, it will raise MLProcessError.
        If this function is invoked in a `try...except...` block,
        raise the MLProcessError outside the starting point of the game process for
        the ProcessManager to stop all processes.

        @param from_ml The name of the ml process
        @param to_wait Whether to wait the object send from the ml process
        @return The received object
        """
        obj = self._comm_to_ml_set.recv(from_ml, to_wait)
        if isinstance(obj, MLProcessError):
            raise obj

        return obj

    def recv_from_all_ml(self, to_wait: bool = False):
        """
        Receive objects from all ml processes

        @param to_wait Whether to wait the object send from the ml processes
        @return A dictionary. The key is the game of the ml process,
                the value is the received object from that process.
        """
        objs = {}
        # Receive the object one by one for the error raising
        # when receiving MLProcessError in `recv_from_ml`
        # instead of using `recv_all` in `CommunicationSet`
        for target_ml in self._comm_to_ml_set.get_recv_end_names():
            objs[target_ml] = self.recv_from_ml(target_ml, to_wait)

        return objs

    # ===== Communication with transition process ===== #

    def set_comm_to_transition(self, recv_end, send_end):
        """
        Set communication objects for communicating with transition process

        @param recv_end The communication object for receiving objects from transition process
        @param send_end the communication object for sending objects to transition process
        """
        self._comm_to_transition.set_recv_end(recv_end)
        self._comm_to_transition.set_send_end(send_end)

    def send_to_transition(self, obj):
        """Send an object to the transition process

        @param obj The object to be sent
        """
        self._comm_to_transition.send(obj)
        # FIXME The exception will not be received immediately.
        # The send() will be stuck (the process is dead) before receiving exception.
        # Set the transition process as the main process to fix it.
        self.check_transition_exception()

    def check_transition_exception(self):
        """Check if there has the exception message sent from the transition process
        """
        if self._comm_to_transition.poll():
            exception = self._comm_to_transition.recv()
            raise exception

class TransitionProcessHelper:
    """
    The helper class for building the transition process
    """
    name = "_transition"

    def __init__(self, server_ip, server_port, channel_name):
        """
        Constructor

        @param server_ip The IP of the remote server
        @param server_port The port of the remote server
        @param channel_name The target communication channel in the remote server
        """
        self.server_ip = server_ip
        self.server_port = server_port
        self.channel_name = channel_name
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

class MLProcessHelper:
    """
    The helper class that helps build ml process

    It is similar to the GameProcessHelper but for the ml process
    """

    def __init__(self, target_module, name, args = (), kwargs = {}):
        """
        Constructor

        @param target_module The full name of the module to be executed in the process.
               The module must have `ml_loop` function.
        @param name The name of the ml process
        @param args The positional arguments to be passed to the `ml_loop`
        @param kwargs The keyword arguments to be passed to the `ml_loop`
        """
        self.target_module = target_module
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self._comm_to_game = CommunicationHandler()

    def set_comm_to_game(self, recv_end, send_end):
        """
        Set communication objects for communicating with game process

        @param recv_end The communication object for receiving objects from game process
        @param send_end The communication object for sending objects to game process
        """
        self._comm_to_game.set_recv_end(recv_end)
        self._comm_to_game.set_send_end(send_end)

    def recv_from_game(self):
        """
        Receive an object from the game process

        @return The received object
        """
        return self._comm_to_game.recv()

    def send_to_game(self, obj):
        """
        Send an object to the game process

        @param obj An object to be sent
        """
        self._comm_to_game.send(obj)

    def send_exception(self, exception: MLProcessError):
        """
        Send an exception to the game process
        """
        self._comm_to_game.send(exception)


def _game_process_entry_point(helper: GameProcessHelper):
    """
    The real entry point of the game process
    """
    # Bind the helper functions to the handlers
    from .communication import base
    base.send_to_ml.set_function(helper.send_to_ml)
    base.send_to_all_ml.set_function(helper.send_to_all_ml)
    base.recv_from_ml.set_function(helper.recv_from_ml)
    base.recv_from_all_ml.set_function(helper.recv_from_all_ml)

    if helper.to_transition:
        base.send_to_transition.set_function(helper.send_to_transition)

    try:
        helper.target_function(*helper.args, **helper.kwargs)
    except (MLProcessError, TransitionProcessError):
        # This exception wil be raised when invoking `recv_from_ml()` and
        # receive `MLProcessError` object from it
        raise
    except Exception:
        raise GameProcessError(helper.name, traceback.format_exc())

def _transition_process_entry_point(helper: TransitionProcessHelper):
    """The entry point of the transition process
    """
    try:
        from .transition import TransitionManager
        transition_manager = TransitionManager( \
            helper.recv_from_game, \
            (helper.server_ip, helper.server_port, helper.channel_name))
        transition_manager.transition_loop()
    except Exception as e:
        exception = TransitionProcessError(helper.name, traceback.format_exc())
        helper.send_exception(exception)

def _ml_process_entry_point(helper: MLProcessHelper):
    """
    The real entry point of the ml process
    """
    # Bind the helper functions to the handlers
    from .communication import base
    base.send_to_game.set_function(helper.send_to_game)
    base.recv_from_game.set_function(helper.recv_from_game)

    try:
        ml_module = importlib.import_module(helper.target_module, __package__)
        ml_module.ml_loop(*helper.args, **helper.kwargs)
    except Exception as e:
        target_script = helper.target_module.split('.')[-1] + ".py"
        trimmed_callstack = trim_callstack(traceback.format_exc(), target_script)
        exception = MLProcessError(helper.name, trimmed_callstack)
        helper.send_exception(exception)
