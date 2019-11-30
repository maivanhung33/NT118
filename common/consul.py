import random
from typing import Optional, Tuple
from urllib.parse import urlparse

from cachetools import TTLCache
from consul import Consul
from injector import singleton, inject
from starlette.config import Config


@singleton
@inject
class ConsulServiceResolver:
    def __init__(self, config: Config, client: Consul) -> None:
        super().__init__()
        self.client = client
        ttl = config('CONSUL_CACHE_TTL',
                     cast=int,
                     default=60)
        self.cache = TTLCache(maxsize=10, ttl=ttl)

    def resolve_url(self, url):
        parsed = urlparse(url)
        if parsed.port is None:
            service = parsed.hostname
            consul_service = self.resolve_service(service)
            if consul_service is None:
                return url
            parsed = parsed._replace(netloc='{}:{}'.format(consul_service[0], consul_service[1]))
        url = parsed.geturl()
        return url

    def resolve_service(self, service: str) -> Optional[Tuple[str, int]]:
        if self.client is None:
            return None
        if service not in self.cache:
            (_, nodes) = self.client.catalog.service(service)
            if len(nodes) == 0:
                raise ValueError('Consul Service doesn\'t  exist')
            node: dict = random.choice(nodes)
            host = node.get('ServiceAddress', '')
            if host is '':
                host = node.get('Address', '')
            port = node.get('ServicePort', '')
            ret = host, port
            self.cache[service] = ret
        return self.cache[service]
