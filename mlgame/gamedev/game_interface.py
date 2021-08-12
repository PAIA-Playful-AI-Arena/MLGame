import abc

from mlgame.view.view_model import Scene


class GameResultState():
    """
    表示遊戲結束的狀態
    finish 表示遊戲有成功執行到最後，表示玩家通關，或是多個玩家至少一人通關
    fail 表示玩家闖關失敗，或是沒有任何一個玩家通關
    """
    FINISH = "FINISH"
    FAIL = "FAIL"


class GameStatus():
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

    def __init__(self):
        self.scene = Scene(width=800, height=600, color="#4FC3F7", bias_x=0, bias_y=0)
        self.frame_count = 0
        self.game_result_state = GameResultState.FAIL

    @abc.abstractmethod
    def update(self, commands):
        self.frame_count += 1

    @abc.abstractmethod
    def game_to_player_data(self) -> dict:
        """
        send something to game AI
        we could send different data to different ai
        """
        to_players_data = {}
        data_to_1p = {
            "frame": self.frame_count,
            "key": "value"

        }

        for ai_client in self.ai_clients():
            to_players_data[ai_client['name']] = data_to_1p
        # should be equal to config. GAME_SETUP["ml_clients"][0]["name"]

        return to_players_data

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

        ai_1p = self.ai_clients()[0]["name"]
        return {ai_1p: cmd_1p}

    @staticmethod
    def ai_clients() -> list:
        """
        let MLGame know how to parse your ai,
        you can also use this names to get different cmd and send different data to each ai client
        """
        return [
            {"name": "1P"}
        ]
