import logging

import consul
from consul import Consul
from injector import Module, singleton, provider
from starlette.config import Config

LOGGER = logging.getLogger(__name__)


class ConsulClientProvider(Module):

    @provider
    @singleton
    def provide_consul_client(self, config: Config) -> Consul:
        enabled = config('CONSUL_ENABLED',
                         cast=bool,
                         default=False)

        if enabled is False:
            return None
        host = config('CONSUL_HOST',
                      cast=str,
                      default='localhost')

        port = config('CONSUL_PORT',
                      cast=int,
                      default=8500)

        scheme = config('CONSUL_SCHEME',
                        cast=str,
                        default='https')
        client = consul.Consul(host=host, port=port, scheme=scheme)
        LOGGER.debug('Consul Client Initialized')
        return client
