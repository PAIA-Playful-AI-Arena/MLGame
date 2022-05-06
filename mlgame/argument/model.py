from os import path
from typing import List, Optional
import pydantic
from pydantic import FilePath, validator, DirectoryPath, Required
import importlib

from mlgame.argument.tool import read_json_file, parse_config
from mlgame.core.exceptions import GameConfigError
from mlgame.utils.logger import logger

CONFIG_FILE_NAME = "config.py"
AI_NAMES = [f"{i}P" for i in range(1, 7)]


class GameConfig:
    """
    The data class storing the game defined config
    """

    def __init__(self, game_folder: str):
        """
        Parse the game defined config and generate a `GameConfig` instance
        """
        game_config = self._load_game_config(game_folder)
        # logger.debug(game_folder)
        config_file = path.join(game_folder, "game_config.json")
        config_data = read_json_file(config_file)

        self.game_version = config_data["version"]
        self.game_params = parse_config(config_data)
        self._process_game_param_dict()

        try:
            self.game_setup = getattr(game_config, "GAME_SETUP")
        except AttributeError:
            raise GameConfigError("Missing 'GAME_SETUP' in the game config")

        # self._process_game_setup_dict()

    def _load_game_config(self, game_folder):
        """
        Load the game config
        """
        try:
            # game_config = importlib.import_module(f"{game_folder}.config")

            spec = importlib.util.spec_from_file_location("config", path.join(game_folder, "config.py").__str__())
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            game_config = module
        except ModuleNotFoundError as e:
            # print which module is not found or installed at which game_folder
            failed_module_name = e.__str__().split("'")[1]
            msg = f"Module '{failed_module_name}' is not found in game process"
            raise GameConfigError(msg)
        else:
            return game_config

    def _process_game_param_dict(self):
        """
        Convert some fields in `GAME_PARAMS`
        """

        # Append the prefix of MLGame.py usage to the `game_usage`
        # and set it to the `usage`
        if self.game_params.get("()") and self.game_params["()"].get("game_usage"):
            game_usage = str(self.game_params["()"].pop("game_usage"))
            # TODO to deprecated
            self.game_params["()"]["usage"] = "python MLGame.py [options] " + game_usage

        # If the game not specify "--version" flag,
        # try to convert `GAME_VERSION` to a flag
        if not self.game_params.get("--version"):
            self.game_params["--version"] = {
                "action": "version",
                "version": self.game_version
            }

class MLGameArgument(pydantic.BaseModel):
    fps: int = 30
    one_shot_mode: bool = False
    ai_clients: Optional[List[FilePath]] = None
    is_manual: bool = False
    no_display: bool = True
    ws_url: pydantic.AnyUrl = None
    game_folder: DirectoryPath
    game_params: List[str]

    # def __init__(self,**kwargs):
    #     self.
    #     self.is_manual = self.ai_clients is None
    @validator('is_manual', always=True)
    def update_manual(cls, v, values) -> bool:
        if 'ai_clients' in values:
            return values['ai_clients'] is None
        return True
