import functools
import time


# Decorator to measure the execution time of a function in milliseconds
def timeit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        execution_time_ms = (end - start) * 1000  # Convert to milliseconds
        print(f"{func.__name__} executed in {execution_time_ms:.4f} ms")
        return result

    return wrapper


# Decorator to measure the execution time of a function in milliseconds using perf_counter
def timeit_in_perf(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        execution_time_ms = (end - start) * 1000  # Convert to milliseconds
        print(f"{func.__name__} executed in {execution_time_ms:.4f} ms")
        return result

    return wrapper
