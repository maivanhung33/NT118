from http import HTTPStatus
from typing import List, Dict

from dataclasses import dataclass
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse


class DomainException(Exception):

    def __init__(self, code: int = 422, message: str = 'Domain Error'):
        self.__code = code
        self.__message = message

    def get_code(self) -> int:
        return self.__code

    def get_message(self) -> str:
        return self.__message


def domain_exception_handler(_, exc: DomainException):
    response = HTTPExceptionResponse(exc.get_code(), exc.get_message(),
                                     errors=[])

    return JSONResponse(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, content=response.__dict__)


class NotFoundException(Exception):
    def __init__(self, code: int = 404, message: str = '404 Not Found'):
        self.__code = code
        self.__message = message

    def get_code(self) -> int:
        return self.__code

    def get_message(self) -> str:
        return self.__message


def not_found_exception_handler(_, exc: NotFoundException):
    response = HTTPExceptionResponse(exc.get_code(), exc.get_message(), errors=[])

    return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content=response.__dict__)


class UnauthenticatedException(Exception):
    def __init__(self, code: int = 401, message: str = 'Unauthenticated'):
        self.__code = code
        self.__message = message

    def get_code(self) -> int:
        return self.__code

    def get_message(self) -> str:
        return self.__message


def unauthenticated_exception_handler(_, exc: UnauthenticatedException):
    response = HTTPExceptionResponse(exc.get_code(), exc.get_message(), errors=[])

    return JSONResponse(status_code=HTTPStatus.UNAUTHORIZED, content=response.__dict__)


class UnauthorizedException(Exception):

    def __init__(self, code: int = 403, message: str = 'Unauthorized'):
        self.__code = code
        self.__message = message

    def get_code(self) -> int:
        return self.__code

    def get_message(self) -> str:
        return self.__message


def unauthorized_exception_handler(_, exc: UnauthorizedException):
    response = HTTPExceptionResponse(exc.get_code(), exc.get_message(), errors=[])

    return JSONResponse(status_code=HTTPStatus.FORBIDDEN, content=response.__dict__)


@dataclass
class HTTPExceptionResponse:
    code: int
    message: str
    errors: List[str]


@dataclass
class ValidationError:
    field: int
    type: str
    message: str


def request_validation_error_handler(_, exc: RequestValidationError):
    errors: List[Dict] = exc.errors()

    def loc_to_field(loc):
        return ','.join(map(lambda e: str(e), list(loc)[1:]))

    validation_errors = [ValidationError(field=loc_to_field(error['loc']),
                                         type=error['loc'][0],
                                         message=error['msg']).__dict__ for error in errors]
    response = HTTPExceptionResponse(400, message='Request Validation Error', errors=validation_errors)

    return JSONResponse(status_code=400, content=response.__dict__)


def http_exception_handler(_, exc: HTTPException):
    response = HTTPExceptionResponse(exc.status_code, message=exc.detail, errors=[])

    return JSONResponse(status_code=exc.status_code, content=response.__dict__)
