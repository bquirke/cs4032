import redis
import zlib

class Cache:
    def __init__(self, host='127.0.0.1', port=6379, db=0):
        self.host = host
        self.port = port
        self.db = db
        self.pool = None
        self.cache = None

    def create_cache(self):
        print("\nCACHE CREATED\n")
        self.pool = redis.ConnectionPool(host=self.host, port=self.port, db=self.db)
        self.cache = redis.Redis(connection_pool=self.pool)

    def get_instance(self):
        return self.cache

    def get_cached(self, key):
        return Cache.decompress(self.cache.get(key))

    def cache_obj(self, key, data):
        self.cache.set(key, Cache.compress(data))

    def delete_obj(self, key):
        self.cache.delete(key)

    def check_cache(self, key):
        return self.cache.exists(key)

    @staticmethod
    def compress(data):
        return zlib.compress(bytes(data, 'utf-8'))

    @staticmethod
    def decompress(data):
        return str(zlib.decompress(data), 'utf-8')