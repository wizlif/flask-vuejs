import time


class MaxCallException(Exception):
    """Exception raised if maximum number of iterations is exceeded"""

    def __init__(self):
        super().__init__('Maximum retries exceeded')


def poll(target, step=2, args=(), kwargs={}, max_tries=None):
    tries = 0

    while True:

        if max_tries is not None and tries >= max_tries:
            raise MaxCallException()

        try:
            val = target(*args, **kwargs)
        except Exception as e:
            print(e)
        else:
            return val

        tries += 1

        time.sleep(step)

