import time

import pytest
from datasets import Dataset

from bforce import timeout_retries, cache_result, clear_cache, TimeoutException

data = {'text': ['I am a sentence', 'Another sentence', 'The last sentence']}
dataset = Dataset.from_dict(data)


# This is the function we will be testing
@timeout_retries(2, max_retries=2)
@cache_result("test_cache")
def func_to_test(batch, sleep_time=1):
    time.sleep(sleep_time)
    # Do some processing on the batch
    processed_batch = {"result": [text + text for text in batch["text"]]}
    return processed_batch


def test_func_to_test():
    # Clear cache before running tests
    clear_cache()

    # First time: calculate and save result to cache
    result_dataset = dataset.map(func_to_test, batched=True)
    assert result_dataset['result'][0] == 'I am a sentenceI am a sentence'

    # Second time: load result from cache
    result_dataset = dataset.map(func_to_test, batched=True)
    assert result_dataset['result'][0] == 'I am a sentenceI am a sentence'

    # Test timeout exception
    with pytest.raises(TimeoutException):
        result_dataset = dataset.map(lambda x: func_to_test(x, sleep_time=6), batched=True)
