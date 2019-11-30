import logging

from fastapi import FastAPI, APIRouter
from injector import singleton, provider, Module, Injector
from starlette.config import Config

from common.controller import ROUTER_KEY
from common.exception import *
from common.utils import fullname

LOGGER = logging.getLogger(__name__)


# Provide FastAPI from configurations
class FastAPIProvider(Module):

    @provider
    @singleton
    def provide(self, config: Config,
                routers: List[APIRouter],
                injector: Injector) -> FastAPI:
        app_title = config('APP_TITLE',
                           cast=str,
                           default=None)
        app_desc = config('APP_DESC',
                          cast=str,
                          default=None)
        app_version = config('APP_VERSION',
                             cast=str,
                             default=None)
        fast_api = FastAPI(title=app_title,
                           description=app_desc,
                           version=app_version)
        fast_api.__injector__ = injector
        self.__register_exception_handler(fast_api)
        for route in routers:
            self.__register_router(fast_api, route)

        LOGGER.debug(fullname(FastAPI) + ' configurated')

        return fast_api

    @staticmethod
    def __register_router(fast_api: FastAPI, router: APIRouter):
        args = {'prefix': ''}
        if hasattr(router, ROUTER_KEY):
            args = getattr(router, ROUTER_KEY)
        fast_api.include_router(router, **args)
        prefix = args['prefix']

    @staticmethod
    def __register_exception_handler(fast_api: FastAPI):
        fast_api.exception_handler(DomainException)(domain_exception_handler)
        fast_api.exception_handler(NotFoundException)(not_found_exception_handler)
        fast_api.exception_handler(RequestValidationError)(request_validation_error_handler)
        fast_api.exception_handler(UnauthenticatedException)(unauthenticated_exception_handler)
        fast_api.exception_handler(UnauthorizedException)(unauthorized_exception_handler)
        fast_api.exception_handler(HTTPException)(http_exception_handler)
