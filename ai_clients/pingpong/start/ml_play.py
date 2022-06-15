_E5_B7_B2_E7_B6_93_E7_99_BC_E7_90_83 = None
_E7_8E_A9_E5_AE_B6_E7_B7_A8_E8_99_9F = None


class MLPlay:
    def __init__(self, ai_name,*args,**kwargs):
        global _E5_B7_B2_E7_B6_93_E7_99_BC_E7_90_83, _E7_8E_A9_E5_AE_B6_E7_B7_A8_E8_99_9F
        _E5_B7_B2_E7_B6_93_E7_99_BC_E7_90_83 = False
        _E7_8E_A9_E5_AE_B6_E7_B7_A8_E8_99_9F = ai_name
        print(ai_name)
    def update(self, scene_info,*args,**kwargs):
        global _E5_B7_B2_E7_B6_93_E7_99_BC_E7_90_83, _E7_8E_A9_E5_AE_B6_E7_B7_A8_E8_99_9F
        if scene_info['status'] != "GAME_ALIVE":
            return "RESET"
        if _E7_8E_A9_E5_AE_B6_E7_B7_A8_E8_99_9F == '1P':
            if not _E5_B7_B2_E7_B6_93_E7_99_BC_E7_90_83:
                _E5_B7_B2_E7_B6_93_E7_99_BC_E7_90_83 = True
                return "SERVE_TO_RIGHT"
            else:
                if scene_info['ball_speed'][0] > 0 or scene_info['ball'][0] > scene_info['platform_1P'][0]:
                    return "MOVE_RIGHT"
                elif scene_info['ball_speed'][0] < 0 or scene_info['ball'][0] < scene_info['platform_1P'][0]:
                    return "MOVE_LEFT"
        elif _E7_8E_A9_E5_AE_B6_E7_B7_A8_E8_99_9F == '2P':
            if not _E5_B7_B2_E7_B6_93_E7_99_BC_E7_90_83:
                _E5_B7_B2_E7_B6_93_E7_99_BC_E7_90_83 = True
                return "SERVE_TO_LEFT"
            else:
                if scene_info['ball_speed'][0] > 0 or scene_info['ball'][0] > scene_info['platform_2P'][0]:
                    return "MOVE_RIGHT"
                elif scene_info['ball_speed'][0] < 0 or scene_info['ball'][0] < scene_info['platform_2P'][0]:
                    return "MOVE_LEFT"
    def reset(self):
        global _E5_B7_B2_E7_B6_93_E7_99_BC_E7_90_83, _E7_8E_A9_E5_AE_B6_E7_B7_A8_E8_99_9F
        _E5_B7_B2_E7_B6_93_E7_99_BC_E7_90_83 = False
