import logging

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from injector import Module, singleton, provider
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

from common.utils import fullname

LOGGER = logging.getLogger(__name__)

# Provide ElasticSearch and ElasticSearch DSL from configurations
class ElasticSearchProvider(Module):

    @provider
    @singleton
    def provide_es_client(self, config: Config) -> Elasticsearch:
        hosts: CommaSeparatedStrings = config('ES_HOSTS',
                                              cast=CommaSeparatedStrings,
                                              default=CommaSeparatedStrings(['http://127.0.0.1:9200']))

        client = Elasticsearch(hosts=hosts)
        LOGGER.debug(fullname(Elasticsearch) + ' configurated')
        return client

    @provider
    @singleton
    def provide_search(self, client: Elasticsearch) -> Search:
        search = Search().using(client=client)

        LOGGER.debug(fullname(Search) + ' configurated')
        return search
