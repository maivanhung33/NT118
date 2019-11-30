import logging
from typing import Set, Type, Dict, Any, List, Sequence, Union, Callable

from fastapi import params, Depends
from injector import singleton, inject
from starlette.responses import JSONResponse, Response

LOGGER = logging.getLogger(__name__)

ROUTER_KEY = '__router__'
ROUTE_KEY = '__route__'


def is_router(cls):
    return hasattr(cls, ROUTER_KEY)


def is_route(cls):
    return hasattr(cls, ROUTE_KEY)


def route(
        path: str,
        *,
        response_model: Type[Any] = None,
        status_code: int = 200,
        tags: List[str] = None,
        dependencies: Sequence[params.Depends] = None,
        summary: str = None,
        description: str = None,
        response_description: str = 'Successful Response',
        responses: Dict[Union[int, str], Dict[str, Any]] = None,
        deprecated: bool = None,
        operation_id: str = None,
        response_model_include: Set[str] = None,
        response_model_exclude: Set[str] = set(),
        response_model_by_alias: bool = True,
        response_model_skip_defaults: bool = False,
        include_in_schema: bool = True,
        response_class: Type[Response] = JSONResponse,
        name: str = None,
) -> Callable:
    return __add_route(
        path=path,
        response_model=response_model,
        status_code=status_code,
        tags=tags or [],
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses or {},
        deprecated=deprecated,
        methods=['GET', 'POST', 'DELETE', 'TRACE', 'PATCH', 'OPTIONS', 'DELETE', 'PUT'],
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_skip_defaults=response_model_skip_defaults,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
    )


def get(
        path: str,
        *,
        response_model: Type[Any] = None,
        status_code: int = 200,
        tags: List[str] = None,
        dependencies: Sequence[params.Depends] = None,
        summary: str = None,
        description: str = None,
        response_description: str = 'Successful Response',
        responses: Dict[Union[int, str], Dict[str, Any]] = None,
        deprecated: bool = None,
        operation_id: str = None,
        response_model_include: Set[str] = None,
        response_model_exclude: Set[str] = set(),
        response_model_by_alias: bool = True,
        response_model_skip_defaults: bool = False,
        include_in_schema: bool = True,
        response_class: Type[Response] = JSONResponse,
        name: str = None,
) -> Callable:
    return __add_route(
        path=path,
        response_model=response_model,
        status_code=status_code,
        tags=tags or [],
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses or {},
        deprecated=deprecated,
        methods=['GET'],
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_skip_defaults=response_model_skip_defaults,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
    )


def put(
        path: str,
        *,
        response_model: Type[Any] = None,
        status_code: int = 200,
        tags: List[str] = None,
        dependencies: Sequence[params.Depends] = None,
        summary: str = None,
        description: str = None,
        response_description: str = 'Successful Response',
        responses: Dict[Union[int, str], Dict[str, Any]] = None,
        deprecated: bool = None,
        operation_id: str = None,
        response_model_include: Set[str] = None,
        response_model_exclude: Set[str] = set(),
        response_model_by_alias: bool = True,
        response_model_skip_defaults: bool = False,
        include_in_schema: bool = True,
        response_class: Type[Response] = JSONResponse,
        name: str = None,
) -> Callable:
    return __add_route(
        path=path,
        response_model=response_model,
        status_code=status_code,
        tags=tags or [],
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses or {},
        deprecated=deprecated,
        methods=['PUT'],
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_skip_defaults=response_model_skip_defaults,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
    )


def post(
        path: str,
        *,
        response_model: Type[Any] = None,
        status_code: int = 200,
        tags: List[str] = None,
        dependencies: Sequence[params.Depends] = None,
        summary: str = None,
        description: str = None,
        response_description: str = 'Successful Response',
        responses: Dict[Union[int, str], Dict[str, Any]] = None,
        deprecated: bool = None,
        operation_id: str = None,
        response_model_include: Set[str] = None,
        response_model_exclude: Set[str] = set(),
        response_model_by_alias: bool = True,
        response_model_skip_defaults: bool = False,
        include_in_schema: bool = True,
        response_class: Type[Response] = JSONResponse,
        name: str = None,
) -> Callable:
    return __add_route(
        path=path,
        response_model=response_model,
        status_code=status_code,
        tags=tags or [],
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses or {},
        deprecated=deprecated,
        methods=['POST'],
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_skip_defaults=response_model_skip_defaults,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
    )


def delete(
        path: str,
        *,
        response_model: Type[Any] = None,
        status_code: int = 200,
        tags: List[str] = None,
        dependencies: Sequence[params.Depends] = None,
        summary: str = None,
        description: str = None,
        response_description: str = 'Successful Response',
        responses: Dict[Union[int, str], Dict[str, Any]] = None,
        deprecated: bool = None,
        operation_id: str = None,
        response_model_include: Set[str] = None,
        response_model_exclude: Set[str] = set(),
        response_model_by_alias: bool = True,
        response_model_skip_defaults: bool = False,
        include_in_schema: bool = True,
        response_class: Type[Response] = JSONResponse,
        name: str = None,
) -> Callable:
    return __add_route(
        path=path,
        response_model=response_model,
        status_code=status_code,
        tags=tags or [],
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses or {},
        deprecated=deprecated,
        methods=['DELETE'],
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_skip_defaults=response_model_skip_defaults,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
    )


def options(
        path: str,
        *,
        response_model: Type[Any] = None,
        status_code: int = 200,
        tags: List[str] = None,
        dependencies: Sequence[params.Depends] = None,
        summary: str = None,
        description: str = None,
        response_description: str = 'Successful Response',
        responses: Dict[Union[int, str], Dict[str, Any]] = None,
        deprecated: bool = None,
        operation_id: str = None,
        response_model_include: Set[str] = None,
        response_model_exclude: Set[str] = set(),
        response_model_by_alias: bool = True,
        response_model_skip_defaults: bool = False,
        include_in_schema: bool = True,
        response_class: Type[Response] = JSONResponse,
        name: str = None,
) -> Callable:
    return __add_route(
        path=path,
        response_model=response_model,
        status_code=status_code,
        tags=tags or [],
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses or {},
        deprecated=deprecated,
        methods=['OPTIONS'],
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_skip_defaults=response_model_skip_defaults,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
    )


def head(
        path: str,
        *,
        response_model: Type[Any] = None,
        status_code: int = 200,
        tags: List[str] = None,
        dependencies: Sequence[params.Depends] = None,
        summary: str = None,
        description: str = None,
        response_description: str = 'Successful Response',
        responses: Dict[Union[int, str], Dict[str, Any]] = None,
        deprecated: bool = None,
        operation_id: str = None,
        response_model_include: Set[str] = None,
        response_model_exclude: Set[str] = set(),
        response_model_by_alias: bool = True,
        response_model_skip_defaults: bool = False,
        include_in_schema: bool = True,
        response_class: Type[Response] = JSONResponse,
        name: str = None,
) -> Callable:
    return __add_route(
        path=path,
        response_model=response_model,
        status_code=status_code,
        tags=tags or [],
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses or {},
        deprecated=deprecated,
        methods=['HEAD'],
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_skip_defaults=response_model_skip_defaults,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
    )


def patch(
        path: str,
        *,
        response_model: Type[Any] = None,
        status_code: int = 200,
        tags: List[str] = None,
        dependencies: Sequence[params.Depends] = None,
        summary: str = None,
        description: str = None,
        response_description: str = 'Successful Response',
        responses: Dict[Union[int, str], Dict[str, Any]] = None,
        deprecated: bool = None,
        operation_id: str = None,
        response_model_include: Set[str] = None,
        response_model_exclude: Set[str] = set(),
        response_model_by_alias: bool = True,
        response_model_skip_defaults: bool = False,
        include_in_schema: bool = True,
        response_class: Type[Response] = JSONResponse,
        name: str = None,
) -> Callable:
    return __add_route(
        path=path,
        response_model=response_model,
        status_code=status_code,
        tags=tags or [],
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses or {},
        deprecated=deprecated,
        methods=['PATCH'],
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_skip_defaults=response_model_skip_defaults,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
    )


def trace(
        path: str,
        *,
        response_model: Type[Any] = None,
        status_code: int = 200,
        tags: List[str] = None,
        dependencies: Sequence[params.Depends] = None,
        summary: str = None,
        description: str = None,
        response_description: str = 'Successful Response',
        responses: Dict[Union[int, str], Dict[str, Any]] = None,
        deprecated: bool = None,
        operation_id: str = None,
        response_model_include: Set[str] = None,
        response_model_exclude: Set[str] = set(),
        response_model_by_alias: bool = True,
        response_model_skip_defaults: bool = False,
        include_in_schema: bool = True,
        response_class: Type[Response] = JSONResponse,
        name: str = None,
) -> Callable:
    return __add_route(
        path=path,
        response_model=response_model,
        status_code=status_code,
        tags=tags or [],
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses or {},
        deprecated=deprecated,
        methods=['TRACE'],
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_skip_defaults=response_model_skip_defaults,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
    )


def __add_route(*args, **kwargs) -> Callable:
    def decorator(fn):
        if not hasattr(fn, ROUTE_KEY):
            setattr(fn, ROUTE_KEY, [])
        getattr(fn, ROUTE_KEY).append({
            'args': args,
            'kwargs': kwargs
        })
        return fn

    return decorator


def router(prefix: str = '',
           tags: List[str] = None,
           dependencies: Sequence[Depends] = None,
           responses: Dict[Union[int, str], Dict[str, Any]] = None):
    arguments = locals()

    def decorator(cls):
        setattr(cls, ROUTER_KEY, arguments)
        return singleton(inject(cls))

    return decorator
