import logging
from typing import Optional, List, Any, Dict

import requests
from dataclasses import dataclass
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from injector import inject, singleton
from requests import RequestException
from starlette.config import Config
from starlette.requests import Request

from common.consul import ConsulServiceResolver
from common.exception import UnauthenticatedException, UnauthorizedException
from common.utils import InjectorUtils

LOGGER = logging.getLogger(__name__)


# OAAth2 Client
@dataclass
class Client:
    client_id: str
    active: bool
    scope: List[str]
    additional_information: dict
    partner_id: Optional[int]


# OAuth2 User
@dataclass
class User:
    principle: Any
    authorities: List[str]
    active: bool
    details: dict


# OAuth2 Base Token Service
class BaseTokenService:
    token_type = 'Bearer'

    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

    def check_error(self, error_map: dict):
        if 'error' in error_map:
            error = error_map['error']
            if isinstance(error, RequestException):
                raise UnauthenticatedException(message='Can\'t connect to authorization server')
            if isinstance(error, dict) and 'message' in error and 'code' in error:
                raise UnauthenticatedException(message=error['message'], code=error['code'])
            if isinstance(error, dict) and 'error' in error:
                raise UnauthenticatedException(message=error['error'])
            if isinstance(error, str):
                raise UnauthenticatedException(message=error)
            raise UnauthenticatedException()


@singleton
@inject
class UserInfoTokenService(BaseTokenService):
    def __init__(self, config: Config, consul_service_resolver: ConsulServiceResolver) -> None:
        self.consul_service_resolver = consul_service_resolver
        endpoint = config('USER_INFO_URL',
                          cast=str,
                          default='http://localhost:8080/userinfo')
        super().__init__(endpoint)

    def load_authentication(self, access_token: str) -> Optional[User]:
        map = self.get_map(access_token)
        self.check_error(map)
        authorities = self.__extract_authorities(map)
        principle = self.__extract_principle(map)
        details = map.get('details', map)
        active = map.get('active', True)
        return User(principle, authorities, active, details)

    def get_map(self, access_token) -> Dict[str, Any]:
        headers = {'Authorization': 'Bearer ' + access_token}
        try:
            url = self.consul_service_resolver.resolve_url(self.endpoint)
            response = requests.get(url, headers=headers)
            if response.status_code is not 200:
                return {'error': response.json()}
            json_response = response.json()
            return json_response
        except Exception as ex:
            return {
                'error': ex
            }

    __AUTHORITY_KEY = ['authority', 'role', 'value']

    def __extract_authority(self, authority):
        for key in self.__AUTHORITY_KEY:
            if key in authority:
                return authority[key]
        return None

    __AUTHORITIES = 'authorities'

    def __extract_authorities(self, obj):
        authorities = self.__AUTHORITIES
        if not isinstance(obj, dict):
            return None
        if authorities in obj and isinstance(obj[authorities], list):
            authorities = [self.__extract_authority(authority) for authority in obj[authorities]]
            return [authority for authority in authorities if authorities is not None]
        for v in obj.values():
            authorities = self.__extract_authorities(v)
            if authorities is not None and not []:
                return authorities
            else:
                return []

    __PRINCIPAL_KEYS = ['user', 'username', 'userid', 'user_id', 'login', 'id', 'name'];

    def __extract_principle(self, map):
        for key in self.__PRINCIPAL_KEYS:
            if key in map:
                return map[key]
        return None


@singleton
@inject
class ClientInfoTokenService(BaseTokenService):

    def __init__(self, config: Config, consul_service_resolver: ConsulServiceResolver) -> None:
        self.consul_service_resolver = consul_service_resolver
        endpoint = config('CLIENT_INFO_URL',
                          cast=str,
                          default='http://localhost:8080/oauth/check_token')
        super().__init__(endpoint)
        LOGGER.debug('ClientInfoTokenService Initialized')

    def load_authentication(self, access_token: str) -> Optional[Client]:
        map = self.get_map(access_token)
        self.check_error(map)
        client_id = map['client_id']
        active = map['active']
        scope = map['scope']
        additional_information = map.get('additional_information', {})
        partner_id = additional_information.get('partner_id', None)
        return Client(client_id, active, scope, additional_information, partner_id)

    def get_map(self, access_token):
        try:
            url = self.consul_service_resolver.resolve_url(self.endpoint)
            response = requests.get(url, params={
                'token': access_token
            })
            if response.status_code is not 200:
                return {'error': response.json()}
            json_response = response.json()
            return json_response
        except Exception as ex:
            LOGGER.exception('exception')
            return {
                'error': ex
            }


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')


def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> User:
    user_info_token_services = InjectorUtils \
        .get_injector(request) \
        .get(UserInfoTokenService)
    user = user_info_token_services.load_authentication(token)
    return user


get_current_user = Depends(get_current_user)


def get_current_client(request: Request, token: str = Depends(oauth2_scheme)) -> Client:
    client_info_token_services = InjectorUtils \
        .get_injector(request) \
        .get(ClientInfoTokenService)
    # client = client_info_token_services.load_authentication('d62d8900-0b55-48ad-bee8-0b11a2082362')
    client = client_info_token_services.load_authentication(token)
    return client


get_current_client: Client = Depends(get_current_client)


def require_user(user: User = get_current_user) -> User:
    if user is None:
        raise UnauthenticatedException()
    if user.active is False:
        raise UnauthenticatedException(message='This user has been disabled')
    return user


require_user = Depends(require_user)


def require_client(client: Client = get_current_client) -> Client:
    if client is None:
        raise UnauthenticatedException()
    if client.active is False:
        raise UnauthenticatedException(message='This client has been disabled')
    return client


require_client = Depends(require_client)


class AuthoritiesChecker:
    def __init__(self, require_authorities: List[str]):
        self.require_authorities = require_authorities

    def __call__(self, user: User = require_user) -> List[str]:
        user_authorites = user.authorities
        for require_authority in self.require_authorities:
            if require_authority not in user_authorites:
                raise UnauthorizedException()
        return user_authorites


def has_authorities(require_authorities: List[str]):
    authorities_checker = AuthoritiesChecker(require_authorities)
    user_authorites: List[str] = Depends(authorities_checker)
    return user_authorites

# def secured(authorites: List[str], partner_id=None):
#     def wrapper(, user=Depends(get_current_user())):
#         if partner_id is not None:
#             return user
#
#     return wrapper
