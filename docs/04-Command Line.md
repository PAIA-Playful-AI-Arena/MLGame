# 指令說明

- 列出 help 文件
  ```shell
  python -m mlgame -h
  ```

- 命令列格式
    ```shell
    python -m mlgame [options] <game_folder> [game_params]
    ```
  - 遊戲執行範例：啟動打磚塊遊戲
    ```shell
    python -m mlgame \
    -f 120 -i ./path/to/ai/ai_client_file_name.py \
    ./path/to/game/arkanoid \
    --difficulty NORMAL --level 3
    ```
    - AI和遊戲的資料夾路徑可以使用`相對路徑`或是`絕對路徑` 
    - 遊戲參數`game_params`須參考各個遊戲 

## 位置引數(Positional Argument)
- `game_folder`
  - `required` 
  - 遊戲資料夾所在的路徑，此路徑下需有`config.py`


## 功能性引數(Functional Argument) 
### `options`
- `--version` 顯示MLGame版本號
- `-h`, `--help`
  - 提供參數的說明
- `-f` `FPS`, `--fps` `FPS`
  - 設定遊戲的遊戲更新率(frame per second)，遊戲預設為每秒更新30次。
  - `default` : `30`
- `-1`, `--one-shot`
  - 表示遊戲只執行一次，沒有加上這個參數，遊戲皆會不斷重新執行。 
  - `default` : `False`
- `--nd`, `--no-display`
  - 加上此參數就不會顯示螢幕畫面。 
  - `default` : `False`
- `--ws_url` `WS_URL`
  - 加上此參數，會建立一個websocket connection，並將遊戲過程中的資料傳到指定的路徑，若路徑失效，則遊戲無法啟動。
- `-i` `AI_Client`, `--input-ai` `AI_Client`
  - 指定要玩遊戲的AI，AI的檔案中，需要包含`MLPlay`這個class。
  - 若有多個玩家，可直接參考下方案例，路徑可以使用絕對路徑與相對路徑。
    ```
    -i ./path/to/ai/ai_01.py -i ./path/to/ai/ai_02.py 
    ```
  - AI數量需符合遊戲需求，每個遊戲都會有最小值與最大值，不足的會以最後一個AI自動補足，多的會自動刪去。
    - 遊戲若需要2個AI，提供1個AI則會同時扮演1P 2P
    - 遊戲若需要2個AI，提供3個AI則會自動排除最後一個

### `game_params`
- `optional` 
- 每個遊戲會在`game_config.json`檔案中，設定不同的遊戲參數
- 若是沒有在指令中提供，將套用參數的預設值
- 格式一律為 `--name_of_params value_of_params`
