import time

_E5_B7_B2_E7_B6_93_E7_99_BC_E7_90_83 = None


class MLPlay:
    def __init__(self):
        global _E5_B7_B2_E7_B6_93_E7_99_BC_E7_90_83
        _E5_B7_B2_E7_B6_93_E7_99_BC_E7_90_83 = False
    def update(self, scene_info):
        global _E5_B7_B2_E7_B6_93_E7_99_BC_E7_90_83
        if scene_info['status'] == "GAME_PASS" or scene_info['status'] == "GAME_OVER":
            return "RESET"
        while True:
            time.sleep(1)
            pass
    def reset(self):
        global _E5_B7_B2_E7_B6_93_E7_99_BC_E7_90_83
        _E5_B7_B2_E7_B6_93_E7_99_BC_E7_90_83 = False