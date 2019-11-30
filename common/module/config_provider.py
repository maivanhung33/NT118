import logging
import os
import sys

from injector import Module, singleton, provider
from starlette.config import Config

LOGGER = logging.getLogger(__name__)


class ConfigProvider(Module):
    @provider
    @singleton
    def provide(self) -> Config:
        env_file = '.env'
        if not os.path.isfile(env_file):
            raise ValueError('\'.env\' file can\'t be found')
        config = Config(env_file)
        self.config_logging(config)
        LOGGER.debug('Config Initialized')
        return config

    def config_logging(self, config: Config):
        log_level = config('LOG_LEVEL',
                           cast=str,
                           default='DEBUG')

        log_format = config('LOG_FORMAT',
                            cast=str,
                            default='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging.basicConfig(level=log_level, format=log_format)
        rootLogger = logging.getLogger()
        # Log INFO to stdout
        h1 = logging.StreamHandler(sys.stdout)
        f1 = SingleLevelFilter(logging.INFO, False)
        h1.addFilter(f1)
        rootLogger.addHandler(h1)
        # Log not INFO to stderr
        h2 = logging.StreamHandler(sys.stderr)
        f2 = SingleLevelFilter(logging.INFO, True)
        h2.addFilter(f2)
        rootLogger.addHandler(h2)


class SingleLevelFilter(logging.Filter):
    def __init__(self, passlevel, reject):
        self.passlevel = passlevel
        self.reject = reject

    def filter(self, record):
        if self.reject:
            return record.levelno != self.passlevel
        else:
            return record.levelno == self.passlevel
