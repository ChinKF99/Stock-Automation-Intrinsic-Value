import time

def sleep_retry(seconds=2):
    """
    Sleep before retrying an API request.
    """
    time.sleep(seconds)