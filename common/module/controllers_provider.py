import inspect
import logging
from typing import List, TypeVar

from boltons.funcutils import wraps
from fastapi.routing import APIRouter
from injector import Module, singleton, multiprovider, Injector, inject

from common.controller import ROUTE_KEY, ROUTER_KEY, is_router

LOGGER = logging.getLogger(__name__)

Controller = TypeVar('Controller')


@inject
@singleton
class ControllerToRouterConverter:
    def __init__(self, injector: Injector) -> None:
        super().__init__()
        self.injector = injector

    def __call__(self, cls: TypeVar) -> APIRouter:
        if not hasattr(cls, ROUTER_KEY):
            raise ValueError('Unexcepted Error')
        router = APIRouter()
        setattr(router, ROUTER_KEY, getattr(cls, ROUTER_KEY))
        members = inspect.getmembers(cls, lambda member: inspect.isfunction(member) and hasattr(member, ROUTE_KEY))
        # members.sort(key=InspectUtils.linenumber_of_member, reverse=True)
        for (fn_name, fn) in members:
            for route_meta in fn.__route__:
                route_inst = self.injector.get(cls)
                _add_route(router, route_inst, route_meta, fn_name)
        return router


def _add_route(router: APIRouter, obj, route: dict, fn_name: str):
    fn = getattr(obj, fn_name)

    @wraps(fn, injected=['self'])
    def wrapper(*args, **kwargs):
        ret = fn(*args, **kwargs)
        return ret

    router.api_route(*route['args'], **route['kwargs'])(wrapper)


# Load and Provide Controllers from 'controller' package
class ControllerProvider(Module):

    @staticmethod
    def __is_common_module(member):
        member_name: str = member.__name__ or member['__name__']
        names = ['requests', 'chardet', 'sys', 'builtins']
        return any([member_name.startswith(name) for name in names])

    def load(self) -> List[Controller]:
        self._tracked_members = set()
        self._router = []
        import controller
        self._load_module(controller)
        return self._router

    def _load_module(self, module=None):
        # members = controller | module, skip common modules
        members = inspect.getmembers(module,
                                     lambda m: m is
                                               not module
                                               and (is_router(m) or inspect.ismodule(m))
                                               and not self.__is_common_module(m))
        for (member_name, member) in members:
            if member in self._tracked_members:
                continue
            else:
                self._tracked_members.add(member)

            if is_router(member):
                self._router.append(member)
            if inspect.ismodule(member):
                self._load_module(member)

    def __init__(self) -> None:
        super().__init__()

    @multiprovider
    @singleton
    def provide_controllers(self) -> List[Controller]:
        controllers = self.load()
        return controllers

    @multiprovider
    @singleton
    def provide_routers(self, converter: ControllerToRouterConverter, controllers: List[Controller]) -> List[APIRouter]:
        routers = [converter(controller) for controller in controllers]
        return routers
