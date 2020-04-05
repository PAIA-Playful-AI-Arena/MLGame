# 乒乓球

## 概觀

<img src="https://i.imgur.com/ke6nUrB.gif" height="500px" />

在回合開始時，可以決定發球位置與方向。如果沒有在 150 影格內發球，球會從平台目前位置隨機往左或往右發球。球速從 7 開始，每 200 影格增加 1。如果球速超過 40 卻還沒分出勝負的話，該回合為平手。

在不同的難度中加入兩種機制。一個是切球，球的 x 方向速度會因為板子接球時的移動而改變；另一個是在場地中央會有一個移動的障礙物。

## 執行

* 手動模式：`python MLGame.py pingpong <difficulty> [game_over_score] -m`
    * 將球發往左邊/右邊：1P - `.`、`/`，2P - `Q`、`E`
    * 移動板子：1P - 左右方向鍵，2P - `A`、`D`
* 機器學習模式：`python MLGame.py pingpong <difficulty> [game_over_score] -i ml_play_template.py`

### 遊戲參數

* `difficulty`：遊戲難度
    * `EASY`：簡單的乒乓球遊戲
    * `NORMAL`：加入切球機制
    * `HARD`：加入切球機制與障礙物
* `game_over_score`：[選填] 指定遊戲結束的分數。當任一方得到指定的分數時，就結束遊戲。預設是 3，但如果啟動遊戲時有指定 `-1` 選項，則結束分數會是 1。

## 詳細遊戲資料

### 座標系

與打磚塊遊戲一樣

### 遊戲區域

500 \* 200 像素。1P 在下半部，2P 在上半部

### 遊戲物件

#### 球

* 5 \* 5 像素大小的綠色正方形
* 每場遊戲開始時，都是由 1P 先發球，之後每個回合輪流發球
* 球由板子的位置發出，可以選擇往左或往右發球。如果沒有在 150 影格內發球，則會自動往隨機一個方向發球
* 初始球速是每個影格 (&plusmn;7, &plusmn;7)，發球後每 200 影格增加 1

#### 板子

* 40 \* 30 的矩形，1P 是紅色的，2P 是藍色的
* 板子移動速度是每個影格 (&plusmn;5, 0)
* 1P 板子的初始位置在 (80, 420)，2P 則在 (80, 50)

#### 切球機制

在板子接球時，球的 x 方向速度會因為板子的移動而改變：

* 如果板子與球往同一個方向移動時，球的 x 方向速度會增加 3 (只增加一次)
* 如果板子沒有移動，則求的 x 方向速度會恢復為目前的基礎速度
* 如果板子與球往相反方向移動時，球會被打回原來過來的方向，其 x 方向速度恢復為目前的基礎速度

切球機制加入在 `NORMAL` 與 `HARD` 難度中。

#### 障礙物

* 30 \* 20 像素的矩形
* 初始位置在 (85, 240)，移動速度為每影格 (&plusmn;3, 0)
* 障礙物會往復移動，初始移動方向是隨機決定的
* 障礙物不會切球，球撞到障礙物會保持球的速度

障礙物加入在 `HARD` 難度中。

## 撰寫玩遊戲的程式

程式範例在 [`ml/ml_play_template.py`](ml/ml_play_template.py)。

### `ml_loop()`

因為乒乓球是兩人遊戲，所以 `ml_loop()` 必須有一個參數 `side`。遊戲會傳 `"1P"` 或 `"2P"` 來幫助辨別函式是被哪一方使用。你可以藉此將兩方遊玩的程式碼寫在同一個檔案中。例如；

```python
def ml_loop(side):
    if side == "1P":
        ml_loop_for_1P()
    else:   # "2P"
        ml_loop_for_2P()
```

### 函式

以下函式定義在 [`games.pingpong.communication`](communication.py) 模組中。

* `ml_ready()`：通知遊戲端已經準備好接收訊息了
* `get_scene_info()`：從遊戲端接接收遊戲場景資訊 `SceneInfo`
* `send_instruction(frame, command)`：傳送指令給遊戲端
    * `frame`：標記這個指令是給哪一個影格的。這個值必須跟收到的 `SceneInfo.frame` 一樣
    * `command`：控制板子的指令，必須是 `PlatformAction` 之一

### 資料結構

以下資料結構已經事先匯入到 [`games.pingpong.communication`](communication.py) 模組中了，可以直接從此模組匯入。

#### `SceneInfo`

儲存遊戲場景資訊。定義在 [`game/gamecore.py`](game/gamecore.py) 中

* `frame`：這個 `SceneInfo` 紀錄的是第幾影格的場景資訊
* `status`：目前的遊戲狀態，會是 `GameStatus` 其中之一
* `ball`：球的位置。為一個 `(x, y)` tuple
* `ball_speed`：目前的球速。為一個 `(x, y)` tuple
* `platform_1P`：1P 板子的位置。為一個 `(x, y)` tuple
* `platform_2P`：2P 板子的位置。為一個 `(x, y)` tuple
* `blocker`：障礙物的位置。為一個 `(x, y)` tuple，如果選擇的難度不是 `HARD`，則其值為 `None`
* `command_1P`：1P 根據這個影格的資訊決定的指令，用在產生紀錄檔中，在遊戲中不會有值
* `command_2P`：同 `command_1P`，但是是 2P 決定的指令

### `GameStatus`

遊戲狀態。定義在 [`game/gamecore.py`](game/gamecore.py) 中

* `GAME_ALIVE`：遊戲正在進行中
* `GAME_1P_WIN`：這回合 1P 獲勝
* `GAME_2P_WIN`：這回合 2P 獲勝
* `GAME_DRAW`：這回合平手

### `PlatformAction`

控制板子的指令。定義在 [`game/gameobject.py`](game/gameobject.py) 中

* `SERVE_TO_LEFT`：將球發向左邊
* `SERVE_TO_RIGHT`：將球發向右邊
* `MOVE_LEFT`：將板子往左移
* `MOVE_RIGHT`：將板子往右移
* `NONE`：無動作

## 機器學習模式的玩家程式

乒乓球是雙人遊戲，所以在啟動機器學習模式時，可以利用 `-i <script_for_1P> <script_for_2P>` 指定兩個不同的玩家程式。如果只有指定一個玩家程式，則兩邊都會使用同一個程式。

而在遊戲中有提供 `ml_play_manual.py` 這個程式，它會建立一個手把，讓玩家可以在機器學習模式中手動與另一個程式對玩。使用流程：

1. 使用 `python MLGame.py pingpong -i ml_play_template.py ml_play_manual.py` 啟動遊戲。會看到有兩個視窗，其中一個就是手把。終端機會輸出 "Invisible joystick is used. Press Enter to start the 2P ml process." 的訊息。

<img src="https://i.imgur.com/iyrS87t.png" height="500px" />

2. 將遊戲手把的視窗拉到一旁，並且讓它是目標視窗 (也就是說視窗的標題不是灰色的)。

<img src="https://i.imgur.com/6kOPjgB.png" height="500px" />

3. 按 Enter 鍵讓手把也發出準備指令以開始遊戲，使用左右方向鍵來控制板子移動。

## 關於球的物理

與打磚塊遊戲的機制相同
