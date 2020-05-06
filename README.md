# MLGame

A platform for applying machine learning algorithm to play pixel games

MLGame separates the machine learning part from the game core, which makes users easily apply codes to play the game. (Support non-python script as the client. Check [here](mlgame/crosslang/README.md) for more information.)

**MLGame Beta 6.0+ is not compatible with the previous version.**

## Requirements

* Python 3.6+
* pygame==1.9.6
* Other machine learning libraries you needed

## Usage

```
$ python MLGame.py [options] <game> [game_params]
```

* `game`: The name of the game to be started. Use `-l` flag to list available games.
* `game_params`: The additional parameters for the game. Use `python MLGame.py <game> -h` to list game parameters of a game.
  * Note that all arguments after `<game>` will be collected to this paremeter
* functional options:
  * `--version`: Show the version number
  * `-h`: Show the help message
  * `-l`: List available games
* game execution options:
  * `-f FPS`: Specify the updating frequency of the game
  * `-m`: Play the game in the manual mode (as a normal game)
  * `-1`: Quit the game when the game is over or is passed. Otherwise, the game will restart automatically.
  * `-r`: Pickle the game progress (a list of "SceneInfo") to log files.
  * `-i SCRIPT [-i SCRIPT ...]`: Specify the script used in the machine learning mode. For multiple scripts, use this flag multiple times. The script must have function `ml_loop()` and be put in the `games/<game>/ml/` directory.

**Game execution options must be specified before &lt;game&gt; arguments.** \
Use `python MLGame.py -h` for more information.

For example:

* List available games:
  ```
  $ python MLGame.py -l
  ```

* List game parameters of the game arkanoid:
  ```
  $ python MLGame.py arkanoid -h
  ```

* Play the game arkanoid level 3 in manual mode on easy difficulty with 45 fps
  ```
  $ python MLGame.py -m -f 45 arkanoid EASY 3
  ```

* Play the game arkanoid level 2 on normal difficulty, record the game progress, and specify the script ml_play_template.py

  ```
  $ python MLGame.py -r -i ml_play_template.py arkanoid NORMAL 2
  ```

## Machine Learning Mode

If `-m` flag is **not** specified, the game will execute in the machine learning mode. In the machine learning mode, the main process will generate two new processes, one is for executing the machine learning code (called ml process), the other is for executing the game core (called game process). They use pipes to communicate with each other.

![Imgur](https://i.imgur.com/NQoXsZf.png)

Scene information is a dictionary object that stores the game status and the position of gameobjects in the scene. Game command is also a dictionary object that stores the command for controlling the gameobject (such as a platform).

### Execution Order

![Imgur](https://i.imgur.com/0yDfdyr.png)

Note that the game process won't wait for the ml process (except for the initialization). Therefore, if the ml process cannot send a game command in time, the command will be consumed in the next frame in the game process, which is "delayed".

The example script for the ml process is in the file `games/<game>/ml/ml_play_template.py`, which is a script that simply sent the same command to the game process. There are detailed comments in the script to describe how to write your own script.

### Non-python Client Support

MLGame supports that a non-python script runs as a ml client. For the supported programming languages and how to use it, please view the [README](mlgame/crosslang/README.md) of the `mlgame.crosslang` module.

### Access Trained Data

The ml script needs to load the trained data from external files. It is recommended that put these files in the same directory of the ml script and use absolute path to access them.

For example, there are two files `ml_play.py` and `trained_data.sav` in the same ml directory:

```python
import os.path
import pickle

def ml_loop():
    dir_path = os.path.dirname(__file__)  # Get the absolute path of the directory of this file in
    data_file_path = os.path.join(dir_path, "trained_data.sav")

    with open(data_file_path, "rb") as f:
        data = pickle.load(f)
```

## Log Game Progress

If `-r` flag is specified, the game progress will be logged into a file. When a game round is ended, a list of "SceneInfo" (i.e. a list of dictionay objects) is dumped to a file `<prefix>_<timestamp>.pickle` by using `pickle.dump()`. The prefix of the filename contains the game mode and game parameters, such as `ml_EASY_2_<timestamp>.pickle`. The file is saved in `games/<game>/log/` directory. These log files can be used to train the model.

### Read Game Progress

You can use `pickle.load()` to read the game progress from the file.

Here is the example for read the game progress:

```python
import pickle
import random

def print_log():
    with open("path/to/log/file", "rb") as f:
        p = pickle.load(f)

    random_id = random.randrange(len(p))
    print(p[random_id])

if __name__ == "__main__":
    print_log()
```

For the non-python client, it may need to write a python script to read the record file and convert the game progess to other format (such as plain text) for the non-python client to read.

## Change Log

View [CHANGELOG.md](./CHANGELOG.md)

## README of the Game

* [arkanoid](games/arkanoid/README.md)
* [pingpong](games/pingpong/README.md)
* [snake](games/snake/README.md)
