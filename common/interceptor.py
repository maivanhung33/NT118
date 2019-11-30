from abc import ABC, abstractmethod
from typing import Callable


class Interceptor(ABC):
    @property
    @abstractmethod
    def pointcut(self) -> object:
        raise NotImplementedError()

    def wraps(self, fn: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            return self.handle(fn, *args, **kwargs)

        return wrapper

    @abstractmethod
    def handle(self, fn: Callable, *args, **kwarg) -> Callable:
        return fn(*args, **kwarg)


def pointcut(key: object):
    def decorator(fn):
        if not hasattr(fn, '__pointcuts__'):
            fn.__pointcuts__ = set()
        fn.__pointcuts__.add(key)
        return fn

    return decorator
