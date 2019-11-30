import logging
import pickle
from typing import Callable, Optional

from injector import singleton, inject
from redis import Redis

from common.interceptor import Interceptor, pointcut

LOGGER = logging.getLogger(__name__)


def default_key_generator(fn: Callable, args, kwargs):
    return str(fn.__qualname__) + str(args) + str(kwargs)


__CACHE__ = object()


@inject
@singleton
class CacheInterceptor(Interceptor):

    def __init__(self, redis: Redis) -> None:
        super().__init__()
        self.redis = redis
        LOGGER.debug('CacheInterceptor Initialized')

    def handle(self, fn: Callable, *args, **kwargs) -> Callable:
        key_generator = getattr(fn, '__cache_key_generator__', None)
        if key_generator is None:
            raise ValueError('key_generator can\'t be None')
        ttl = getattr(fn, '__cache_ttl__', None)
        key = key_generator(fn, args, kwargs)
        if self.redis.exists(key) == 0:
            ret = super().handle(fn, *args, *kwargs)
            self.redis.append(key, pickle.dumps(ret))
            if ttl is not None:
                self.redis.expire(key, ttl)
            return ret
        return pickle.loads(self.redis.get(key))

    @property
    def pointcut(self):
        return __CACHE__


def cache(ttl: Optional[int] = None, key_generator: Callable = default_key_generator):
    def decorator(fn):
        fn.__cache_key_generator__ = key_generator
        if ttl is not None:
            fn.__cache_ttl__ = ttl
        fn = pointcut(__CACHE__)(fn)
        return fn

    return decorator
