# Arkanoid 打磚塊

## 概觀

<img src="https://i.imgur.com/brqaW85.gif" height="500"/>

回合一開始，可以決定發球的位置與方向。發球後嘗試接到回彈的球，並打掉所有磚塊。

打磚塊有兩個難度：簡單與普通，在普通難度中會加入切球的機制，可以在板子接球的時候，藉由移動板子來改變球的速度或方向。在一些關卡內有紅色的硬磚塊，需要打兩次才能被破壞，但是透過切球來加速球的移動速度，則可以打一次就破壞該磚塊。

## 執行

* 手動模式：`python MLGame.py arkanoid <difficulty> <level_id> -m`
    * 將球發到左邊/右邊：`A` 或 `D`
    * 移動板子：左右方向鍵
* 機器學習模式：`python MLGame.py arkanoid <difficulty> <level_id> -i ml_play_template.py`

### 遊戲參數

* `difficulty`：遊戲難度
    * `EASY`：簡單的打磚塊遊戲
    * `NORMAL`：加入切球機制
* `level_id`：指定關卡地圖。可以指定的關卡地圖皆在 `game/level_data/` 裡

## 詳細遊戲資訊

### 座標系

使用 pygame 的座標系統，原點在遊戲區域的左上角，x 正方向為向右，y 正方向為向下。遊戲物件的座標皆在物件的左上角，並非中心點。

### 遊戲區域

200 \* 500 像素

### 遊戲物件

#### 球

* 5 \* 5 像素的藍色方形
* 每一影格的移動速度是 (&plusmn;7, &plusmn;7)
* 球會從板子所在的位置發出，可以選擇往左或往右發球。如果在 150 影格內沒有發球，則會自動往隨機兩個方向發球

#### 板子

* 40 \* 5 像素的綠色長方形
* 每一影格的移動速度是 (&plusmn;5, 0)
* 初始位置在 (75, 400)

#### 切球機制

球的 x 方向速度會因為接球時板子的移動方向而改變：

* 如果板子與球的移動方向相同，則球的 x 方向速度會增為 &plusmn;10，可以一次打掉硬磚塊
* 如果板子不動，則球的 x 方向速度會回復為 &plusmn;7
* 如果板子與球的移動方向相反，則球會被打回原來來的方向，速度會回復為 &plusmn;7

此機制加入在普通難度中。

#### 磚塊

* 25 \* 10 的橘色長方形
* 其位置由關卡地圖決定

#### 硬磚塊

* 與磚塊類似，但是紅色的
* 硬磚塊要被打兩次才會被破壞。其被球打一次後，會變為一般磚塊。但是如果被加速後的球打到，則可以直接被破壞

## 撰寫玩遊戲的程式

範例程式在 [`ml/ml_play_template.py`](ml/ml_play_template.py)

### 函式

以下函式定義在 [`games.arkanoid.communication`](communication.py) 模組中

* `ml_ready()`：通知遊戲端已經準備好了。呼叫此函式後遊戲端才會開始傳送訊息
* `get_scene_info()`：從遊戲端接收遊戲場景資訊 `SceneInfo`
* `send_instruction(frame, command)`：傳送指令給遊戲端
    * `frame`：標記這個指令是給哪一個影格的。這個值必須跟收到的 `SceneInfo.frame` 一樣
    * `command`：控制板子的指令，必須是 `PlatformAction` 其中之一

### 資料結構

以下資料結構都已經先匯入到 [`games.arkanoid.communication`](communication.py) 中

#### `SceneInfo`

儲存遊戲場景的資訊。定義在 [`game/gamecore.py`](game/gamecore.py)。

`SceneInfo` 的成員：

* `frame`：這個 `SceneInfo` 紀錄的是第幾影格的場景資訊
* `status`：目前的遊戲狀態，會是 `GameStatus` 其中之一
* `ball`：球的位置。為一個 `(x, y)` tuple
* `platform`：平台的位置。為一個 `(x, y)` tuple
* `bricks`：剩餘的普通磚塊的位置，包含被打過一次的硬磚塊。為一個 list，裡面每個元素皆為 `(x, y)` tuple
* `hard_bricks`：剩餘的硬磚塊位置。為一個 list，裡面每個元素皆為 `(x, y)` tuple
* `command`：依照這個影格的場景資訊而決定的指令。用於產生紀錄檔，在遊戲中沒有用途

#### `GameStatus`

遊戲狀態。定義在 [`game/gamecore.py`](game/gamecore.py)

一共有三種遊戲狀態：

* `GAME_ALIVE`：遊戲進行中
* `GAME_PASS`：所有磚塊都被破壞
* `GAME_OVER`：平台無法接到球

#### `PlatformAction`

控制平台的移動。定義在 [`game/gameobject.py`](game/gameobject.py)

一共有五種指令：

* `SERVE_TO_LEFT`：將球發往左邊
* `SERVE_TO_RIGHT`：將球發往右邊
* `MOVE_LEFT`：將平台往左移動
* `MOVE_RIGHT`：將平台往右移動
* `NONE`：平台無動作

## 自訂關卡地圖

你可以將自訂的關卡地圖放在 `game/level_data/` 裡，並給其一個獨特的 `<level_id>.dat` 作為檔名。

在地圖檔中，每一行由三個數字構成，分別代表磚塊的 x 和 y 座標，與磚塊類型。檔案的第一行是標記所有方塊的座標補正 (offset)，因此方塊的最終座標為指定的座標加上第一行的座標補正。而磚塊類型的值，0 代表一般磚塊，1 代表硬磚塊，而第一行的磚塊類型值永遠是 -1，例如：
```
25 50 -1
10 0 0
35 10 0
60 20 1
```
代表這個地圖檔有三個磚塊，其座標分別為 (35, 50)、(60, 60),、(85, 70)，而第三個磚塊是硬磚塊。

## 關於球的物理

如果球撞進其他遊戲物件或是遊戲邊界，球會被直接「擠出」到碰撞面上，而不是補償碰撞距離給球。

![Imgur](https://i.imgur.com/ouk3Jzh.png)
