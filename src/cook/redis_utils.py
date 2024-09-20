import redis
from django.conf import settings


class RedisHandler:
    def __init__(self):
        self.redis_client = redis.StrictRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
        )

    def get_value_from_key(self, key):
        """
        Redisからフォームの数を取得
        """
        result = self.redis_client.get(key)

        if result is None:
            raise KeyError(
                "Could'nt find key {} from redis server".format(key)
            )

        return result

    def set_key_and_value(self, key, value):
        """
        Redisにフォームの数を保存
        """
        self.redis_client.set(key, value)
