from typing import List, Optional
import pydantic
from pydantic import FilePath, validator, DirectoryPath, Required
import importlib
from mlgame.core.exceptions import GameConfigError

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

        self.game_version = getattr(game_config, "GAME_VERSION", "")
        self.game_params = getattr(game_config, "GAME_PARAMS", {
            "()": {
                "prog": game_folder,
                "game_usage": "%(prog)s"
            }
        })
        self._process_game_param_dict()

        try:
            self.game_setup = getattr(game_config, "GAME_SETUP")
        except AttributeError:
            raise GameConfigError("Missing 'GAME_SETUP' in the game config")

        self._process_game_setup_dict()

    def _load_game_config(self, game_folder):
        """
        Load the game config
        """
        try:
            # game_config = importlib.import_module(f"{game_folder}.config")

            spec = importlib.util.spec_from_file_location("config", f"{game_folder}/config.py")
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
        param_dict = self.game_params

        # Append the prefix of MLGame.py usage to the `game_usage`
        # and set it to the `usage`
        if param_dict.get("()") and param_dict["()"].get("game_usage"):
            game_usage = str(param_dict["()"].pop("game_usage"))
            # TODO to deprecated
            param_dict["()"]["usage"] = "python MLGame.py [options] " + game_usage

        # If the game not specify "--version" flag,
        # try to convert `GAME_VERSION` to a flag
        if not param_dict.get("--version"):
            param_dict["--version"] = {
                "action": "version",
                "version": self.game_version
            }

    def _process_game_setup_dict(self):
        """
        Process the value of `GAME_SETUP`

        The `GAME_SETUP` is a dictionary which has several keys:
        - "game": Specify the class of the game to be execute
        - "dynamic_ml_clients": (Optional) Whether the number of ml clients is decided by
          the number of input scripts.
        - "ml_clients": A list containing the information of the ml client.
            Each element in the list is a dictionary in which members are:
            - "name": A string which is the name of the ml client.
            - "args": (Optional) A tuple which contains the initial positional arguments
                to be passed to the ml client.
            - "kwargs": (Optional) A dictionary which contains the initial keyword arguments
                to be passed to the ml client.
        """
        try:
            game_cls = self.game_setup["game"]
            # ml_clients = self.game_setup["ml_clients"]
        except KeyError as e:
            raise GameConfigError(
                f"Missing {e} in 'GAME_SETUP' in '{CONFIG_FILE_NAME}'")

        # Check if the specified name is existing or duplicated
        ml_names = []
        # for client in ml_clients:
        #     client_name = client.get("name", "")
        #     if not client_name:
        #         raise GameConfigError(
        #             "'name' in 'ml_clients' of 'GAME_SETUP' "
        #             f"in '{CONFIG_FILE_NAME}' is empty or not existing")
        #     if client_name in ml_names:
        #         raise GameConfigError(
        #             f"Duplicated name '{client_name}' in 'ml_clients' of 'GAME_SETUP' "
        #             f"in '{CONFIG_FILE_NAME}'")
        #     ml_names.append(client_name)

        # if not self.game_setup.get("dynamic_ml_clients"):
        #     self.game_setup["dynamic_ml_clients"] = False
        #
        # if self.game_setup["dynamic_ml_clients"] and len(ml_clients) == 1:
        #     print(
        #         f"Warning: 'dynamic_ml_clients' in 'GAME_SETUP' in '{CONFIG_FILE_NAME}' "
        #         "is invalid for just one ml client. Set to False.")
        #     self.game_setup["dynamic_ml_clients"] = False


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
