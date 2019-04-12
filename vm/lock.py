from time import sleep
import uuid

RELEASE_LUA_SCRIPT = """
    if redis.call("get",KEYS[1]) == ARGV[1] then
        return redis.call("del",KEYS[1])
    else
        return 0
    end
"""


class LocalLock(object):
    """https://redis.io/topics/distlock"""

    def __init__(self, lock_key):
        self.lock_key = lock_key
        self.lock_value = None
        self.retry_times = 15
        self.retry_delay = 1
        self.ttl = 10000

        from redis import StrictRedis

        connection = {
            'host': 'localhost',
            'port': 6379,
            'password': None,
            'db': 1,
        }

        self.node = StrictRedis(**connection)

    def __enter__(self):
        if not self.acquire():
            raise Exception('failed to acquire lock')

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

    def acquire_node(self):
        return self.node.set(self.lock_key, self.lock_value, nx=True, px=self.ttl)

    def release_node(self):
        self.node.register_script(RELEASE_LUA_SCRIPT)(keys=[self.lock_key], args=[self.lock_value])

    def acquire(self):
        self.lock_value = uuid.uuid4().hex

        for retry in range(self.retry_times):
            if self.acquire_node():
                return True
            else:
                sleep(self.retry_delay)
        return False

    def release(self):
        self.release_node()


def lock(lock_key):
    return LocalLock(lock_key)
