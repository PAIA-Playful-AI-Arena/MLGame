# MLGame

A platform for applying machine learning algorithm to play pixel games

MLGame separates the machine learning part from the game core, which makes users easily apply codes to play the game. (Support non-python script as the client. Check [here](mlgame/crosslang/README.md) for more information.)

For the concept and the API of the MLGame, visit the [wiki page](https://github.com/LanKuDot/MLGame/wiki) of this repo (written in Traditional Chinese).

# Requirements

* Python==3.9
* pygame==2.0.1
* Other machine learning libraries you needed

# TODO 
- [ ] document
- [x] arkanoid pingpong easy_game
- [x] update maze_car game cmd
- [ ] test case
- [ ] update error handler 

# Change
1. 啟動命令
2. 專案架構
3. 新增ws 
4. 

# Usage

```shell
python -m mlgame [options] <game_folder> [game_params]
```
A platform for applying machine learning algorithm to play pixel games. In default, the game runs in the machine learning mode.

## Positional arguments:
  - `game_folder`
    - `required` 
    - the name of the game to be started
  - `game_params`
    - `optional` 
    - the additional settings for the game. Note that all arguments after <game> will be collected to
                            `game_params`.

## functional options:
  - `--version`             show program's version number and exit
  - `-h`, `--help`
    - Show this help message and exit. If this flag is specified after the <game>, show the help message of the game instead.
  - `-f` `FPS`, `--fps` `FPS`
    - The updating frequency of the game process
    - `default` : `30`
  - `-1`, `--one-shot`
    - Quit the game when the game is passed or is over. Otherwise, the game will restart automatically. 
    - `default` : `False`
  - `--nd`, `--no-display`    didn't display the game on screen. 
    - `default` : `False`
  - `--ws_url` `WS_URL`       ws_url route
  - `-i` `SCRIPT`, `--input-ai` `SCRIPT`
    - Specify user script(s) for the machine learning mode.
    - For multiple user scripts, use this flag multiple times.
    - The script path could be relative path or absolute path

## Command Line example:

- List game parameters of the game arkanoid:
  ```shell
  python -m mlgame -h
  ```

- Play the game arkanoid level 3 on normal difficulty with 120 fps
  ```shell
  python -m mlgame \
  -f 120 -i ./AI_Code/arkanoid/rule/ml_play.py \
  ./games/arkanoid \
  --difficulty NORMAL --level 3
  ```

### Read Instruction

The game provides README files for detailed information, such as:

* How to execute and play the game
* The information of game objects
* The format of the scene information and the game command

Here are README of games:

* [arkanoid](games/arkanoid/README.md)
* [pingpong](games/pingpong/README.md)
* [snake](games/snake/README.md)

### `MLPlay` class

The scripts for playing the game must have a `MLPlay` class and provide the corresponding functions. Here is a template of the `MLPlay` class:

```python
class MLPlay:
    def __init__(self, init_arg_1, init_arg_2, ...):
        ...

    def update(self, scene_info):
        ...

    def reset(self):
        ...
```

* `__init__(self, init_arg_1, init_arg_2, ...)`: The initialization of `MLPlay` class, such as loading trained module or initializing the member variables
  * `init_arg_x`: The initial arguments sent from the game.
* `update(self, scene_info) -> command or "RESET"`: Handle the received scene information and generate the game command
  * `scene_info`: The scene information sent from the game.
  * `command`: The game command sent back to the game.
  * If the `scene_info` contains a game over message, return `"RESET"` instead to make MLGame invoke `reset()`.
* `reset(self)`: Do some reset stuffs for the next game round

### Non-python Client Support

MLGame supports that a non-python script runs as a ml client. For the supported programming languages and how to use it, please view the [README](mlgame/crosslang/README.md) of the `mlgame.crosslang` module.

## Record Game Progress

If `-r` flag is specified, the game progress will be recorded into a file, which is saved in `games/<game_name>/log/` directory. When a game round is ended, a file `<prefix>_<timestamp>.pickle` is generated. The prefix of the filename contains the game mode and game parameters, such as `ml_EASY_2_2020-09-03_08-05-23.pickle`. These log files can be used to train the model.

### Format

The dumped game progress is a dictionary. The first key is `"record_format_version"` which indicates the format version of the record file, and its value is 2 for the current mlgame version. The other keys are the name of ml clients which are defined by the game. Its value is also a dictionary which has two keys - `"scene_info"` and `"command"`. They sequentially stores the scene information and the command received or sent from that ml client. Note that the last element of `"command"` is always `None`, because there is no command to be sent when the game is over.

The game progress will be like:

```
{
    "record_format_version": 2,
    "ml_1P": {
        "scene_info": [scene_info_0, scene_info_1, ... , scene_info_n-1, scene_info_n],
        "command": [command_0, command_1, ... , command_n-1, None]
    },
    "ml_2P": {
        "scene_info": [scene_info_0, scene_info_1, ... , scene_info_n-1, scene_info_n],
        "command": [command_0, command_1, ... , command_n-1, None]
    },
    "ml_3P": {
        "scene_info": [],
        "command": []
    }
}
```

If the scene information is not privided for the certain ml client, which the game runs with dynamic ml clients, it's value will be an empty list like "ml_3P" in the above example.

### Read Game Progress

You can use `pickle.load()` to read the game progress from the file.

Here is the example for read the game progress:

```python
import pickle
import random

def print_log():
    with open("path/to/log/file", "rb") as f:
        p = pickle.load(f)

    print("Record format version:", p["record_format_version"])
    for ml_name in p.keys():
        if ml_name == "record_format_version":
            continue

        target_record = p[ml_name]
        random_id = random.randrange(len(target_record["scene_info"]))
        print("Scene information:", target_record["scene_info"][random_id])
        print("Command:", target_record["command"][random_id])

if __name__ == "__main__":
    print_log()
```

> For the non-python client, it may need to write a python script to read the record file and convert the game progess to other format (such as plain text) for the non-python client to read.

### Access Trained Data

The ml script needs to load the trained data from external files. It is recommended that put these files in the same directory of the ml script and use absolute path to access them.

For example, there are two files `ml_play.py` and `trained_data.sav` in the same ml directory:

```python
from pathlib import Path
import pickle

class MLPlay:
    def __init__(self):
        # Get the absolute path of the directory in where this file is
        dir_path = Path(__file__).parent
        data_file_path = dir_path.joinpath("trained_data.sav")

        with open(data_file_path, "rb") as f:
            data = pickle.load(f)
```

## Change Log

View [CHANGELOG.md](./CHANGELOG.md)
