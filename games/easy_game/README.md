# **Easy Game**

[comment]: <> (![python]&#40;https://img.shields.io/pypi/pyversions/pygame&#41;)
![pygame](https://img.shields.io/badge/release-1.1.1-red.svg)

[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![MLGame](https://img.shields.io/badge/MLGame-9.4.0-<COLOR>.svg)](https://github.com/PAIA-Playful-AI-Arena/MLGame)
[![pygame](https://img.shields.io/badge/pygame-2.0.1-<COLOR>.svg)](https://github.com/pygame/pygame/releases/tag/2.0.1)


這是一個吃東西小遊戲，也是 PAIA 的遊戲教學範例

![https://github.com/PAIA-Playful-AI-Arena/MLGame/raw/master/games/easy_game/asset/easy_game.gif](https://github.com/PAIA-Playful-AI-Arena/MLGame/raw/master/games/easy_game/asset/easy_game.gif)

---
# 基礎介紹

## 啟動方式

- 直接啟動 [main.py](http://main.py) 即可執行

### 遊戲參數設定

```python
# main.py 
game = EasyGame(time_to_play=1000, total_point_count=10, score=5, color="FF9800")
```

- `time_to_play`：遊戲執行的終止時間，單位是 frame，也就是遊戲內部更新畫面的次數，每更新一次 frame +1
- `total_point_count`：遊戲中食物出現的最大數量。
- `score`：遊戲通關的點數，要超過這個分數才算過關。
- `color`：主角方塊的顏色，使用16進位顏色表示法

## 玩法

- 使用鍵盤 上、下、左、右 控制方塊

## 目標

1. 在遊戲時間截止前，盡可能吃到愈多的食物吧！

### 通關條件

1. 時間結束前，吃到的食物超過`score`，即可過關。

### 失敗條件

1. 時間結束前，吃到的食物少於`score`，即算失敗。

## 遊戲系統

1. 行動機制
    
    上下左右的行動，每次移動`10.5px`
    
2. 座標系統
    - 螢幕大小 800 x 600
    - 主角方塊 50 x 50
    - 食物方塊 8 x 8

---

# 進階說明

## 使用ＡＩ玩遊戲

```bash
# python MLGame.py [options] easy_game [time_to_play] [total_point_count] [score] [color]
python MLGame.py -i ml_play_template.py easy_game --time_to_play 1200 --total_point_count 15 --score 10 --color FF9800
```

遊戲參數依序是[`time_to_play`] [`total_point_count`] [`score`] [`color`]

## ＡＩ範例

```python
import random

class MLPlay:
    def __init__(self):
        print("Initial ml script")

    def update(self, scene_info: dict):

        # print("AI received data from game :", scene_info)

        actions = ["UP", "DOWN", "LEFT", "RIGHT", "NONE"]

        return random.sample(actions, 1)

    def reset(self):
        """
        Reset the status
        """
        print("reset ml script")
        pass
```

## 遊戲資訊

- scene_info 的資料格式如下

```json
{
  "frame": 25,
  "ball_x": 425,
  "ball_y": 306,
  "foods": [
    {
      "x": 656,
      "y": 210
    },
...,
    {
      "x": 371,
      "y": 217
    }
    
  ],
  "score": 0,
  "status": "GAME_ALIVE"
}
```

- `frame`：遊戲畫面更新的編號
- `ball_x`：主角方塊的Ｘ座標，表示方塊的左邊座標值。
- `ball_y`：主角方塊的Ｙ座標，表示方塊的上方座標值。
- `foods`：食物的清單，清單內每一個物件都是一個食物的左上方座標值
- `score`：目前得到的分數
- `status`： 目前遊戲的狀態
    - `GAME_ALIVE`：遊戲進行中
    - `GAME_PASS`：遊戲通關
    - `GAME_OVER`：遊戲結束

## 動作指令

- 在 update() 最後要回傳一個字串，主角物件即會依照對應的字串行動，一次只能執行一個行動。
    - `UP`：向上移動
    - `DOWN`：向下移動
    - `LEFT`：向左移動
    - `RIGHT`：向右移動
    - `NONE`：原地不動

## 遊戲結果

- 最後結果會顯示在console介面中，若是PAIA伺服器上執行，會回傳下列資訊到平台上。

```json
{
  "frame_used": 100,
  "state": "FAIL",
  "attachment": [
    {
      "player": "1P",
      "score": 0,
      "rank": 1
    }
  ]
}
```

- `frame_used`：表示使用了多少個frame
- `state`：表示遊戲結束的狀態
    - `FAIL`：遊戲失敗
    - `FINISH`：遊戲完成
- `attachment`：紀錄遊戲各個玩家的結果與分數等資訊
    - `player`：玩家編號
    - `score`：吃到的食物總數
    - `rank`：排名

---