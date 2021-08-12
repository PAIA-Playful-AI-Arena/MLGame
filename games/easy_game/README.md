# Easy Game
這是一個簡單的遊戲，主要用來示範如何在PAIA 上發布一個遊戲

## Game Config
遊戲參數定義檔案需要使用json格式，且需要命名為`game_config.json`
```json
{
  "game_name": "easy_game", // 遊戲的名稱
  "version": "1.0.1", // 版本號
  "url": "None", // github 專案連結
  "game_params": [ // 遊戲參數陣列
    {
      "name": "time_to_play", // 遊戲參數的名字
      "verbose": "遊戲總幀數", // 顯示文字
      "type": "int", // 類型 分為 int str
      "max": 2000, // int 可以設定 最大最小值
      "min": 600,
      "default": 600, // 遊戲參數的預設值
//     參數的輔助說明
      "help": "set the limit of frame count , actually time will be revised according to your FPS .",
      
    },
    {
      "name": "color",
      "verbose": "矩形顏色",
      "type": "str",
      "choices": [
//        字串的選項需要有顯示文字(verbose) 與 實際值(value)
        {
          "verbose": "CYAN",
          "value": "00BCD4"
        },
        {
          "verbose": "YELLOW",
          "value": "FFEB3B"
        },
        {
          "verbose": "ORANGE",
          "value": "FF9800"
        }
      ],
      "help": "set the color of rectangle",
      "default": "FFEB3B"
    }
  ]
}
```
## Game Blockly
```json

```
## Game interface
遊戲的入口需要

## Flowchart

## Create a new game