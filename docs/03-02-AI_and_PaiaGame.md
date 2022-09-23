# AI
ＡＩ檔案中須包含`MLPlay` 這個Class，並實作下方三個method  
```python
class MLPlay:
    def __init__(self,ai_name, *args, **kwargs):
        ...

    def update(self, scene_info, *args, **kwargs):
        ...

    def reset(self):
        ...
```
- 初始化 `__init__(self,ai_name, *args, **kwargs)`
  - `ai_name` 為遊戲AI的編號，ex `1P`, `2P`...
  - 可使用 `kwargs['game_params']` 取得啟動遊戲參數資訊，可用來判斷遊戲的模式。ex 乒乓球的普通模式與困難模式
    - `kwargs['game_params']`為`dict`物件，key 須參考遊戲中 `game_config.json`檔案。 
  - 建議在此函式中載入ＡＩ模型
- 產生遊戲指令 `update(self, scene_info, *args, **kwargs):`
  - 需回傳遊戲所需要的命令
- 重置ＡＩ `reset(self)`

# PaiaGame
遊戲檔案中須繼承`PaiaGame` 這個Class，並實作下方六/七個method
```python
class PaiaGame(abc.ABC):
    def __init__(self, user_num: int, *args, **kwargs):...

    @abc.abstractmethod
    def update(self, commands: dict):...

    @abc.abstractmethod
    def get_data_from_game_to_player(self) -> dict:...

    @abc.abstractmethod
    def reset(self):...

    @abc.abstractmethod
    def get_scene_init_data(self) -> dict:...
    
    @abc.abstractmethod
    def get_scene_progress_data(self) -> dict:...
    
    @abc.abstractmethod
    def get_game_result(self) -> dict:...

```
- 初始化 `__init__(self, user_num: int, *args, **kwargs)`
  - `user_num` 為遊戲遊玩的人數，ex `1`, `2`...
  - 可使用 `kwargs['game_params']` 取得啟動遊戲參數資訊，可用來新增遊戲設定
    - `kwargs['game_params']`為`dict`物件，key 須參考遊戲中 `game_config.json`檔案。 
  - 建議在此函式中載入遊戲模型
- 更新遊戲狀態 `update(self, commands: dict):`
  - `commands` 為所有ＡＩ回傳命令，ex `{"1P": ["UP"], "2P": ["DOWN", "SHOOT"], ...}`
  - 若要重置遊戲，需回傳遊戲重置命令 `"RESET"`
  - 若要結束遊戲，需回傳遊戲結束命令 `"QUIT"`
- 獲取遊戲資料給ＡＩ`get_data_from_game_to_player(self):`
  - ex 
    ```json
    {
      "1P": 
      {
        "frame": 0,
        "x": 0, 
        "y": 0, 
        "walls": [], 
        "key": "value",
        "..."
      }, 
      "2P": 
      {
      "..."
      }
    }
    ```
- 重置遊戲 `reset(self)`
- 獲取遊戲場景初始化資料 `get_scene_init_data`
  - 用於初始化遊戲視窗，建立遊戲圖片資料庫
- 獲取遊戲場景更新資料 `get_scene_progress_data`
  - 用於更新遊戲畫面
- 獲取遊戲結果資料 `get_game_result`
  - 用於遊戲結束或重置時，輸出此回合的遊戲結果

[//]: # (## Class 結構)
[//]: # (## 資料格式)
[//]: # (## Decorator)
[//]: # (function name and data structure)
