import pickle
import threading
import os
import atexit
from functools import wraps
import hashlib
import json
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


def make_cache_key(func, args, kwargs):
    func_name = func.__name__.encode()
    args_data = pickle.dumps(args)
    kwargs_data = pickle.dumps(kwargs)
    key = func_name + args_data + kwargs_data
    return hashlib.sha256(key).hexdigest()


class cache_result:
    def __init__(self, cache_dir="cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        self.cache = self.load_cache(cache_dir)
        atexit.register(self.save_all)  # Save cache when program exits

    def save_cache(self, cache_key, cache_value):
        try:
            self.cache[cache_key] = dict(cache_value)
        except TypeError:  # If data is not serializable
            self.cache[cache_key] = cache_value

    def save_all(self):
        for cache_key, cache_value in self.cache.items():
            file_path = os.path.join(self.cache_dir, f"{cache_key}.json")
            with open(file_path, "w") as f:
                json.dump(cache_value, f)

    def load_cache(self, cache_dir):
        if not os.path.exists(cache_dir):
            return {}
        cache = {}
        file_count = 0  # Count the number of files loaded
        for filename in os.listdir(cache_dir):
            file_path = os.path.join(cache_dir, filename)
            if filename.endswith('.json'):
                with open(file_path, "r") as f:
                    try:
                        cache_value = json.load(f)
                        file_count += 1  # Increment the counter if the file is successfully loaded
                    except json.JSONDecodeError:
                        print(f"Cannot load JSON from {file_path}. Skipping this file.")
                        continue
                    cache_key = filename.split(".")[0]  # Remove the extension
                    cache[cache_key] = cache_value
        print(f"Loaded {file_count} files from the cache directory")  # Print the number of files loaded
        return cache

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = make_cache_key(func, args, kwargs)
            if cache_key in self.cache:
                print(f"Loading result for {func.__name__} from cache")
                return self.cache[cache_key]
            else:
                result = func(*args, **kwargs)
                print(f"Caching result for {func.__name__}")
                self.save_cache(cache_key, result)
                return result

        return wrapper