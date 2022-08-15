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
  - ai_name為遊戲AI的編號，ex `1P`, `2P`...
  - 可使用 `kwargs['game_params']` 取得啟動遊戲參數資訊，可用來判斷遊戲的模式。ex 乒乓球的普通模式與困難模式
    - `kwargs['game_params']`為`dict`物件，key 須參考遊戲中 `game_config.json`檔案。 
  - 建議在此函式中載入ＡＩ模型
- 產生遊戲指令 `update(self, scene_info, *args, **kwargs):`
  - 需回傳遊戲所需要的命令
- 重置遊戲 `reset(self)`

# PaiaGame
## Class 結構
## 資料格式

[//]: # (function name and data structure)
