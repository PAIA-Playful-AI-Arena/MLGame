# 操作教學

## 安裝方法
1. 預備環境
   - 此框架僅能在 python 3.9 中運行。
2. 透過 pypi 安裝
  - https://pypi.org/project/mlgame/
    ```shell
      pip install mlgame
    ```
  - 指定特定版本
    ```shell
      pip install mlgame==9.5.3.2
    ```

> 安裝好python環境與mlgame框架之後，即可開始進行此教學。

## 下載遊戲
1. 在終端機下載遊戲，並進入遊戲資料夾。
   - 以下載打磚塊遊戲為例
   ```shell
      git clone git@github.com:PAIA-Playful-AI-Arena/arkanoid.git
      #   or
      # git clone https://github.com/PAIA-Playful-AI-Arena/arkanoid.git
      cd arkanoid
    ```
2. 下載遊戲原始碼，解壓縮，並在遊戲資料夾中打開終端機。
![](./assets/download-arkanoid.png)

[//]: # (TODO )

## 啟動遊戲
- 啟動打磚塊遊戲
    ```shell 
    python -m mlgame \
    -f 120 \
    -i ./ml/ml_play_template.py \
    . \
    --difficulty NORMAL --level 3
    ```
  > - 指令中的路徑在遊戲資料夾中，使用者須參考自身情況調整遊戲資料夾與ＡＩ資料夾
  > - AI和遊戲的資料夾路徑可以使用 **相對路徑** 或 **絕對路徑** 
  > - 遊戲參數`game_params`請參考各個遊戲

[//]: # (TODO 遊戲圖片)

