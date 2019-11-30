from typing import List

from injector import Module, multiprovider

from common.cache import CacheInterceptor
from common.interceptor import Interceptor


# Provide default interceptors
class InterceptorProvider(Module):

    def __init__(self) -> None:
        super().__init__()

    @multiprovider
    def provide_controllers(self, cache: CacheInterceptor) -> List[Interceptor]:
        interceptors = [cache]
        return interceptors
