from common.module.amqp_publisher_provider import AMQPPublisherProvider
from common.module.config_provider import ConfigProvider
from common.module.consul_client_provider import ConsulClientProvider
from common.module.controllers_provider import ControllerProvider
from common.module.elastic_search_provider import ElasticSearchProvider
from common.module.fast_api_provider import FastAPIProvider
from common.module.interceptor_provider import InterceptorProvider
from common.module.mongo_client_provider import MongoClientProvider
from common.module.redis_provider import RedisProvider

modules = [ConfigProvider,
           MongoClientProvider,
           ConsulClientProvider,
           InterceptorProvider,
           FastAPIProvider,
           AMQPPublisherProvider,
           RedisProvider,
           ControllerProvider,
           ElasticSearchProvider]
