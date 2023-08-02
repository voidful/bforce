import json
import os
import pickle
import threading
import uuid
from functools import wraps

from .exceptions import TimeoutException


def timeout_retries(seconds, max_retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(max_retries):
                res = [TimeoutException('function [%s] timeout [%s seconds]' % (func.__name__, seconds))]

                def newFunc():
                    try:
                        res[0] = func(*args, **kwargs)
                    except Exception as e:
                        res[0] = e

                t = threading.Thread(target=newFunc)
                t.daemon = True
                try:
                    t.start()
                    t.join(seconds)
                except Exception as je:
                    print('error starting thread')
                    raise je
                ret = res[0]
                if not isinstance(ret, BaseException):
                    return ret
                else:
                    print(f"Exception: {str(ret)}")
                    print(f"Function {func.__name__} timeout, retrying...")

            raise TimeoutException(f"Function {func.__name__} exceeded maximum retries")

        return wrapper

    return decorator


def clear_cache(cache_dir="cache"):
    if os.path.exists(cache_dir):
        for filename in os.listdir(cache_dir):
            file_path = os.path.join(cache_dir, filename)
            os.remove(file_path)


def save_cache(cache_key, cache_value, cache_dir="cache"):
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    try:
        file_path = os.path.join(cache_dir, f"{uuid.uuid4().hex}.json")
        with open(file_path, "w") as f:
            json.dump((cache_key, cache_value), f)
    except TypeError:  # If data is not JSON serializable, use pickle
        file_path = os.path.join(cache_dir, f"{uuid.uuid4().hex}.pkl")
        with open(file_path, "wb") as f:
            pickle.dump((cache_key, cache_value), f)
    return file_path


def load_cache(cache_dir="cache"):
    if not os.path.exists(cache_dir):
        return {}
    cache = {}
    for filename in os.listdir(cache_dir):
        file_path = os.path.join(cache_dir, filename)
        try:
            if filename.endswith('.json'):
                with open(file_path, "r") as f:
                    cache_key, cache_value = json.load(f)
            elif filename.endswith('.pkl'):
                with open(file_path, "rb") as f:
                    cache_key, cache_value = pickle.load(f)
            else:
                continue
            cache[cache_key] = cache_value
        except (json.JSONDecodeError, ValueError, pickle.UnpicklingError) as e:
            print(f"Error in file: {file_path}. Skipping this file.")
            print(f"Error message: {e}")
            with open(file_path, "r") as f:
                print(f"Content: {f.read()}")
    return cache


def cache_result(cache_dir="cache"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Load cache
            cache = load_cache(cache_dir)
            # Create a key based on function name and arguments
            cache_key = f"{func.__name__}_{args}_{kwargs}"
            if cache_key in cache:
                # print(f"Loaded result from cache for function: {func.__name__} with args: {args} and kwargs: {kwargs}")
                return cache[cache_key]
            else:
                result = func(*args, **kwargs)
                # Save result to cache
                save_cache(cache_key, result, cache_dir)
                return result

        return wrapper

    return decorator
