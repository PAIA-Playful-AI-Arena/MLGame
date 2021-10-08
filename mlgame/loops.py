"""
The loop executor for running games and ml client
"""

import importlib
from re import M
import time
import traceback
import sys

from .gamedev.game_interface import PaiaGame
from .view.view import PygameView
from .communication import GameCommManager, MLCommManager
from .exceptions import GameProcessError, MLProcessError
from .gamedev.generic import quit_or_esc
from .recorder import get_recorder


class GameManualModeExecutor:
    """
    The loop executor for the game process running in manual mode
    """

    def __init__(self, execution_cmd, game_cls, ml_names):
        self._execution_cmd = execution_cmd
        self._game_cls = game_cls
        self._ml_names = ml_names
        self._frame_interval = 1 / self._execution_cmd.fps
        self._fps = self._execution_cmd.fps
        self._recorder = get_recorder(execution_cmd, ml_names)

    def start(self):
        """
        Start the loop for running the game
        """
        try:
            self._loop()
        except Exception:
            raise GameProcessError("game", traceback.format_exc())

    def _loop(self):
        """
        The main loop for running the game
        """
        game = self._game_cls(*self._execution_cmd.game_params)
        assert isinstance(game, PaiaGame), "Game " + str(game) + " should implement a abstract class : PaiaGame"

        scene_init_info_dict = game.get_scene_init_data()
        game_view = PygameView(scene_init_info_dict)
        while not quit_or_esc():
            scene_info_dict = game.game_to_player_data()
            time.sleep(self._frame_interval)
            # pygame.time.Clock().tick_busy_loop(self._fps)
            cmd_dict = game.get_keyboard_command()
            self._recorder.record(scene_info_dict, cmd_dict)

            result = game.update(cmd_dict)
            view_data = game.get_scene_progress_data()
            game_view.draw_screen()
            game_view.draw(view_data)
            game_view.flip()

            if result == "RESET" or result == "QUIT":
                scene_info_dict = game.game_to_player_data()
                self._recorder.record(scene_info_dict, {})
                self._recorder.flush_to_file()
                print(game.get_game_result())
                if self._execution_cmd.one_shot_mode or result == "QUIT":
                    break

                game.reset()


class GameMLModeExecutorProperty:
    """
    The data class that helps build `GameMLModeExecutor`
    """

    def __init__(self, proc_name, execution_cmd, game_cls, ml_names):
        """
        Constructor

        @param proc_name The name of the process
        @param execution_cmd A `ExecutionCommand` object that contains execution config
        @param game_cls The class of the game to be executed
        @param ml_names The name of all ml clients
        """
        self.proc_name = proc_name
        self.execution_cmd = execution_cmd
        self.game_cls = game_cls
        self.ml_names = ml_names
        self.comm_manager = GameCommManager()


class GameMLModeExecutor:
    """
    The loop executor for the game process running in ml mode
    """

    def __init__(self, propty: GameMLModeExecutorProperty):
        self._proc_name = propty.proc_name
        self._execution_cmd = propty.execution_cmd
        self._game_cls = propty.game_cls
        self._ml_names = propty.ml_names
        self._comm_manager = propty.comm_manager

        # Get the active ml names from the created ml processes
        self._active_ml_names = list(self._comm_manager.get_ml_names())
        self._dead_ml_names = []
        self._ml_execution_time = 1 / self._execution_cmd.fps
        self._fps = self._execution_cmd.fps
        self._ml_delayed_frames = {}
        for name in self._active_ml_names:
            self._ml_delayed_frames[name] = 0
        self._recorder = get_recorder(self._execution_cmd, self._ml_names)
        self._frame_count = 0

    def start(self):
        """
        Start the loop for the game process
        """
        try:
            self._loop()
        except MLProcessError:
            # This exception wil be raised when invoking `GameCommManager.recv_from_ml()`
            # and receive `MLProcessError` object from it
            raise
        except Exception:
            raise GameProcessError(self._proc_name, traceback.format_exc())

    def _loop(self):
        """
        The loop for sending scene information to the ml process, received the command
        sent from the ml process, and pass command to the game for execution.
        """
        game = self._game_cls(*self._execution_cmd.game_params)
        assert isinstance(game, PaiaGame), "Game " + str(game) + " should implement a abstract class : PaiaGame"
        scene_init_info_dict = game.get_scene_init_data()
        game_view = PygameView(scene_init_info_dict)
        self._wait_all_ml_ready()
        while not quit_or_esc():
            scene_info_dict = game.game_to_player_data()
            cmd_dict = self._make_ml_execute(scene_info_dict)
            self._recorder.record(scene_info_dict, cmd_dict)

            result = game.update(cmd_dict)
            self._frame_count += 1
            view_data = game.get_scene_progress_data()
            # TODO add a flag to determine if draw the screen
            game_view.draw_screen()
            game_view.draw(view_data)
            game_view.flip()

            if len(self._active_ml_names) == 0:
                raise MLProcessError(self._proc_name, 
                                     "The process {} exit because all ml processes has exited.".
                                     format(self._proc_name))

            # Do reset stuff
            if result == "RESET" or result == "QUIT":
                scene_info_dict = game.game_to_player_data()
                # send to ml_clients and don't parse any command , while client reset ,
                # self._wait_all_ml_ready() will works and not blocks the process
                for ml_name in self._active_ml_names:
                    self._comm_manager.send_to_ml(scene_info_dict[ml_name], ml_name)
                # TODO check what happen when bigfile is saved
                time.sleep(0.1)
                self._recorder.record(scene_info_dict, {})
                self._recorder.flush_to_file()
                print(game.get_game_result())

                if self._execution_cmd.one_shot_mode or result == "QUIT":
                    break

                game.reset()
                self._frame_count = 0
                # TODO think more
                for name in self._active_ml_names:
                    self._ml_delayed_frames[name] = 0
                self._wait_all_ml_ready()

    def _wait_all_ml_ready(self):
        """
        Wait until receiving "READY" commands from all ml processes
        """
        # Wait the ready command one by one
        for ml_name in self._active_ml_names:
            recv = self._comm_manager.recv_from_ml(ml_name)
            if isinstance(recv, MLProcessError):
                print(recv.message)
                self._dead_ml_names.append(ml_name)
                self._active_ml_names.remove(ml_name)
                continue
            while recv != "READY":
                recv = self._comm_manager.recv_from_ml(ml_name)

    def _make_ml_execute(self, scene_info_dict) -> dict:
        """
        Send the scene information to all ml processes and wait for commands

        @return A dict of the recevied command from the ml clients
                If the client didn't send the command, it will be `None`.
        """
        try:
            for ml_name in self._active_ml_names:
                self._comm_manager.send_to_ml(scene_info_dict[ml_name], ml_name)
        except KeyError as e:
            raise KeyError(
                "The game doesn't provide scene information "
                f"for the client '{ml_name}'")

        time.sleep(self._ml_execution_time)
        response_dict = self._comm_manager.recv_from_all_ml()
        
        cmd_dict = {}
        for ml_name in self._active_ml_names[:]:
            cmd_received = response_dict[ml_name]
            if isinstance(cmd_received, MLProcessError):
                print(cmd_received.message)
                self._dead_ml_names.append(ml_name)
                self._active_ml_names.remove(ml_name)
            elif isinstance(cmd_received, dict):
                self._check_delay(ml_name, cmd_received["frame"])
                cmd_dict[ml_name] = cmd_received["command"]
            else:
                cmd_dict[ml_name] = None

        for ml_name in self._dead_ml_names:
            cmd_dict[ml_name] = None

        return cmd_dict

    def _check_delay(self, ml_name, cmd_frame):
        """
        Check if the timestamp of the received command is delayed
        """
        delayed_frame = self._frame_count - cmd_frame
        if delayed_frame > self._ml_delayed_frames[ml_name]:
            self._ml_delayed_frames[ml_name] = delayed_frame
            print("The client '{}' delayed {} frame(s)".format(ml_name, delayed_frame))


class MLExecutorProperty:
    """
    The data class that helps build `MLExecutor`
    """

    def __init__(self, name, target_module, init_args=(), init_kwargs={}):
        """
        Constructor

        @param target_module The full name of the module to be executed in the process.
               The module must have `ml_loop` function.
        @param name The name of the ml process
        @param init_args The positional arguments to be passed to the `MLPlay.__init__()`
        @param init_kwargs The keyword arguments to be passed to the `MLPlay.__init__()`
        """
        self.name = name
        self.target_module = target_module
        self.init_args = init_args
        self.init_kwargs = init_kwargs
        self.comm_manager = MLCommManager(name)


class MLExecutor:
    """
    The loop executor for the machine learning process
    """

    def __init__(self, propty: MLExecutorProperty):
        self._name = propty.name
        self._target_module = propty.target_module
        self._init_args = propty.init_args
        self._init_kwargs = propty.init_kwargs
        self._comm_manager = propty.comm_manager
        self._frame_count = 0

    def start(self):
        """
        Start the loop for the machine learning process
        """
        self._comm_manager.start_recv_obj_thread()

        try:
            self._loop()
        except Exception:
            exception = MLProcessError(self._name,
                                       "The process '{}' is exited by itself. {}"
                                       .format(self._name, traceback.format_exc()))
            self._comm_manager.send_to_game(exception)
            sys.exit()

        #except SystemExit:  # Catch the exception made by 'sys.exit()'
        #    exception = MLProcessError(self._name,
        #                               "The process '{}' is exited by itself. {}"
        #                               .format(self._name, traceback.format_exc()))
        #    self._comm_manager.send_to_game(exception)

    def _loop(self):
        """
        The loop for receiving scene information from the game, make ml class execute,
        and send the command back to the game.
        """
        ml_module = importlib.import_module(self._target_module, __package__)
        ml = ml_module.MLPlay(*self._init_args, **self._init_kwargs)
        
        self._ml_ready()
        while True:
            scene_info = self._comm_manager.recv_from_game()
            if scene_info is None:
                # game over
                break
            command = ml.update(scene_info)
            # print(command)
            if command == "RESET":
                # TODO refactor reset method
                ml.reset()
                self._frame_count = 0
                self._ml_ready()
                continue

            if command is not None:
                self._comm_manager.send_to_game({
                    "frame": self._frame_count,
                    "command": command
                })

            self._frame_count += 1

        # Stop the client of the crosslang module
        if self._target_module == "mlgame.crosslang.ml_play":
            ml.stop_client()

    def _ml_ready(self):
        """
        Send a "READY" command to the game process
        """
        self._comm_manager.send_to_game("READY")
