import redis

from order_api.config import envs


redis = redis.Redis(host=envs.REDIS_URL, port=6379, db=0)
