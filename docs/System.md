# 系統架構

# Game

# AI

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
