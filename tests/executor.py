import importlib
import os
import time

import pandas as pd
import pygame

from mlgame.communication import GameCommManager, MLCommManager
from mlgame.exceptions import MLProcessError
from mlgame.gameconfig import GameConfig
from mlgame.gamedev.game_interface import PaiaGame
from mlgame.gamedev.generic import quit_or_esc
from mlgame.utils.argparser_generator import get_parser_from_dict
from mlgame.utils.enum import KEYS
from mlgame.view.view import PygameView


class AIClientExecutor():
    def __init__(self, ai_client_path, ai_comm: MLCommManager):
        self._frame_count = 0
        self.ai_comm = ai_comm
        self.ai_path = ai_client_path
        self._proc_name = ai_client_path

    def run(self):
        self.ai_comm.start_recv_obj_thread()
        module_name = os.path.basename(self.ai_path)
        spec = importlib.util.spec_from_file_location(module_name, self.ai_path)
        self.__module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.__module)
        # TODO add init args
        # self.ml = self.__module.MLPlay(*self._init_args, **self._init_kwargs)
        self.ml = self.__module.MLPlay()
        # cmd = self.ml.update({})
        print("             AI Client runs")
        self._ml_ready()
        while True:
            scene_info, keyboard_info = self.ai_comm.recv_from_game()
            if scene_info is None:
                # game over
                break
            # assert keyboard_info == "1"
            command = self.ml.update(scene_info, keyboard_info)
            if scene_info["status"] != "GAME_ALIVE" or command == "RESET":
                command = "RESET"
                # self.ml.reset()
                self._frame_count = 0
                self._ml_ready()
                continue

            if command is not None:
                # 收到資料就回傳
                self.ai_comm.send_to_game({
                    "frame": self._frame_count,
                    "command": command
                })

            self._frame_count += 1

        # Stop the client of the crosslang module
        if self.__module == "mlgame.crosslang.ml_play":
            self.ml.stop_client()
        print("             AI Client ends")

    def _ml_ready(self):
        """
        Send a "READY" command to the game process
        """
        self.ai_comm.send_to_game("READY")


class GameExecutor():
    def __init__(self, game_folder: str, game_params, game_comm: GameCommManager, fps=30, one_shot_mode=False):
        self.frame_count = 0
        self.game_comm = game_comm
        game_config = GameConfig(game_folder)
        param_parser = get_parser_from_dict(game_config.game_params)
        parsed_game_params = param_parser.parse_args(game_params)
        self.game_params = parsed_game_params.__dict__
        game_setup = game_config.game_setup
        self._game_cls = game_setup["game"]

        # game_cls = game_setup["game"]
        # game = game_cls(**parsed_game_params.__dict__)
        # assert isinstance(game, PaiaGame), "Game " + str(game) + " should implement a abstract class : PaiaGame"

        self._active_ml_names = []
        self._ml_delayed_frames = {}
        self._active_ml_names = list(self.game_comm.get_ml_names())
        self._dead_ml_names = []
        self._ml_execution_time = 1 / fps
        self._fps = fps
        self._ml_delayed_frames = {}
        for name in self._active_ml_names:
            self._ml_delayed_frames[name] = 0
        # self._recorder = get_recorder(self._execution_cmd, self._ml_names)
        self._frame_count = 0
        self.one_shot_mode = one_shot_mode
        self._proc_name = "game"

    def run(self):
        # TODO use ai client and return cmd to game
        # TODO catch exception
        # print("game executor runs")
        # while self.frame_count < 10:
        #     print(f"game executor runs at {self.frame_count}")
        #     self.frame_count += 1
        #     if self.frame_count % 2 == 0:
        #         self.game_comm.send_to_all_ml(({"status": "GAME_ALIVE"}, "keyboard_info"))
        #     recv = self.game_comm.recv_from_all_ml()
        #     print(f"game receive {recv}")
        #     time.sleep(0.2)
        game = self._game_cls(**self.game_params)
        assert isinstance(game, PaiaGame), "Game " + str(game) + " should implement a abstract class : PaiaGame"
        scene_init_info_dict = game.get_scene_init_data()
        game_view = PygameView(scene_init_info_dict)
        self._wait_all_ml_ready()
        while not quit_or_esc():
            scene_info_dict = game.game_to_player_data()
            keyboard_info = []
            pressed_keys = pygame.key.get_pressed()
            if True in pressed_keys:
                for k in KEYS:
                    if pressed_keys[k]:
                        keyboard_info.append(k)

            cmd_dict = self._make_ml_execute(scene_info_dict, keyboard_info)
            # self._recorder.record(scene_info_dict, cmd_dict)

            result = game.update(cmd_dict)
            self._frame_count += 1
            view_data = game.get_scene_progress_data()
            # TODO add a flag to determine if draw the screen
            game_view.draw(view_data)

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
                    self.game_comm.send_to_ml((scene_info_dict[ml_name], []), ml_name)
                # TODO check what happen when bigfile is saved
                time.sleep(0.1)
                # self._recorder.record(scene_info_dict, {})
                # self._recorder.flush_to_file()
                # print(json.dumps(game.get_game_result(), indent=2))
                attachments = game.get_game_result()['attachment']
                print(pd.DataFrame(attachments).to_string())

                if self.one_shot_mode or result == "QUIT":
                    break

                game.reset()
                game_view.reset()

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
            recv = self.game_comm.recv_from_ml(ml_name)
            if isinstance(recv, MLProcessError):
                print(recv.message)
                self._dead_ml_names.append(ml_name)
                self._active_ml_names.remove(ml_name)
                continue
            while recv != "READY":
                recv = self.game_comm.recv_from_ml(ml_name)

    def _make_ml_execute(self, scene_info_dict, keyboard_info) -> dict:
        """
        Send the scene information to all ml processes and wait for commands

        @return A dict of the recevied command from the ml clients
                If the client didn't send the command, it will be `None`.
        """
        try:
            for ml_name in self._active_ml_names:
                self.game_comm.send_to_ml((scene_info_dict[ml_name], keyboard_info), ml_name)
        except KeyError as e:
            raise KeyError(
                "The game doesn't provide scene information "
                f"for the client '{ml_name}'")

        time.sleep(self._ml_execution_time)
        response_dict = self.game_comm.recv_from_all_ml()

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
