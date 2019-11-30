import logging

import redis
from injector import singleton, provider, Module
from redis import Redis
from starlette.config import Config

LOGGER = logging.getLogger(__name__)

# Provide Redis Client from configuration
class RedisProvider(Module):
    @provider
    @singleton
    def provide(self, config: Config) -> Redis:
        redis_host = config('REDIS_URL',
                            cast=str,
                            default='localhost')

        redis_port = config('REDIS_PORT',
                            cast=int,
                            default=6379)

        client = redis.StrictRedis(host=redis_host, port=redis_port,
                                decode_responses=False)
        LOGGER.debug('Redis Client Initialized')
        return client
