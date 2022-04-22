
import time
from mlgame.communication import GameCommManager, MLCommManager

class AIClientExecutor():
    def __init__(self, ai_comm:MLCommManager):
        self.frame_count = 0
        self.ai_comm = ai_comm

    def run(self):
        self.ai_comm.start_recv_obj_thread()
        print("             AI Client runs")
        while self.frame_count < 10:
            print(f"             AI Client runs at {self.frame_count}")

            recv = self.ai_comm.recv_from_game()
            if recv:
                print(f"             AI Client receive: {recv}")
                self.ai_comm.send_to_game(f"Hi it's ai({self.frame_count:3d})")
                self.frame_count += 1
            # time.sleep(0.1)


class GameExecutor():
    def __init__(self, game_comm: GameCommManager):
        self.frame_count = 0
        self.game_comm = game_comm


    def run(self):
        # TODO use ai client and return cmd to game
        print("game executor runs")
        while self.frame_count < 10:
            print(f"game executor runs at {self.frame_count}")
            self.frame_count += 1
            self.game_comm.send_to_all_ml(f"hi it is game({self.frame_count:3d})")
            recv = self.game_comm.recv_from_all_ml()
            print(f"game receive {recv}")
            time.sleep(0.2)
