import _winapi

from mlgame.execution import execute
import multiprocessing as mp

if __name__ == "__main__":
    # if not _winapi:
    #     mp.set_start_method('spawn')
    execute()
