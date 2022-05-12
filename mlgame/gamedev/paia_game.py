import abc
from mlgame.utils.enum import get_ai_name
from mlgame.view.view_model import Scene


class GameResultState():
    """
    表示遊戲結束的狀態
    finish 表示遊戲有成功執行到最後，表示玩家通關，或是多個玩家至少一人通關
    fail 表示玩家闖關失敗，或是沒有任何一個玩家通關
    """
    FINISH = "FINISH"
    FAIL = "FAIL"
    # TODO refactor


class GameStatus():
    # TODO refactor
    """
        表示遊戲進行中的狀態
        GAME_ALIVE 表示遊戲進行中
        GAME_OVER 表示玩家闖關失敗，多人遊戲中，收到此狀態，表示輸掉此遊戲
        GAME_PASS 表示玩家闖關成功，多人遊戲中，收到此狀態，表示贏得此遊戲
    """
    GAME_ALIVE = "GAME_ALIVE"
    GAME_OVER = "GAME_OVER"
    GAME_PASS = "GAME_PASS"
    GAME_1P_WIN = "GAME_1P_WIN"
    GAME_2P_WIN = "GAME_2P_WIN"
    GAME_DRAW = "GAME_DRAW"


class PaiaGame(abc.ABC):
    def __init__(self, user_num: int, *args, **kwargs):
        self.scene = Scene(width=800, height=600, color="#4FC3F7", bias_x=0, bias_y=0)
        self.frame_count = 0
        self.game_result_state = GameResultState.FAIL
        self.user_num = user_num

    @abc.abstractmethod
    def update(self, commands):
        self.frame_count += 1

    @abc.abstractmethod
    def get_data_from_game_to_player(self) -> dict:
        """
        send something to game AI
        we could send different data to different ai
        """
        data_to_player = {}
        data_to_1p = {
            "frame": self.frame_count,
            "key": "value"

        }
        for i in range(self.user_num):
            data_to_player[get_ai_name(i)] = data_to_1p
        return data_to_player

    @abc.abstractmethod
    def reset(self):
        pass

    @abc.abstractmethod
    def get_scene_init_data(self) -> dict:
        """
        Get the initial scene and object information for drawing on the web
        """
        # TODO add music or sound
        scene_init_data = {"scene": self.scene.__dict__,
                           "assets": [

                           ],
                           # "audios": {}
                           }
        return scene_init_data

    @abc.abstractmethod
    def get_scene_progress_data(self) -> dict:
        """
        Get the position of game objects for drawing on the web
        """

        scene_progress = {
            # background view data will be draw first
            "background": [],
            # game object view data will be draw on screen by order , and it could be shifted by WASD
            "object_list": [],
            "toggle": [],
            "foreground": [],
            # other information to display on web
            "user_info": [],
            # other information to display on web
            "game_sys_info": {}
        }
        return scene_progress

    @abc.abstractmethod
    def get_game_result(self) -> dict:
        """
        send game result
        """
        return {"frame_used": self.frame_count,
                "result": {

                },

                }

    @abc.abstractmethod
    def get_keyboard_command(self) -> dict:
        """
        Define how your game will run by your keyboard
        """
        cmd_1p = []

        return {get_ai_name(0): cmd_1p}


def get_paia_game_obj(game_cls, parsed_game_params: dict, user_num) -> PaiaGame:
    game = game_cls(user_num=user_num, **parsed_game_params)
    assert isinstance(game, PaiaGame), "Game " + str(game) + " should implement a abstract class : PaiaGame"
    return game
