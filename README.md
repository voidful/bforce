# BForce Library

The BForce(BruteForce) library is designed to facilitate complex computation that may require retries or caching for efficient execution. The library consists of decorators that can be easily applied to functions to achieve the desired functionality.

## Getting Started

### Prerequisites
- Python 3.6 or above

### Installation

To install the library, clone the repository and install it using pip:

```bash
pip install bforce
```

## Usage

Here are the main features of the library:

### Timeout and Retries

The `@timeout_retries` decorator allows a function to be retried if it doesn't complete within a specified time limit.

```python
from bforce import timeout_retries


@timeout_retries(timeout=2, max_retries=2)
def my_function(arg1, arg2):
# Your code here
```

In the example above, if `my_function` does not complete within 2 seconds, it will be retried up to 2 times.

### Caching Results

The `@cache_result` decorator can be used to cache the result of a function. This is especially useful for time-consuming functions where you want to avoid computing the same result multiple times.

```python
from bforce import cache_result


@cache_result("my_cache")
def my_function(arg1, arg2):
# Your code here
```

In the above example, the result of `my_function` will be saved in "my_cache". If the function is called again with the same arguments, the cached result will be returned instead of running the function again.

### Clearing Cache

You can clear the cache using the `clear_cache()` function:

```python
from bforce import clear_cache

clear_cache("my_cache")
```

This will clear all entries in "my_cache".

## Running the Tests

To run the tests, use the following command:

```bash
pytest
```
