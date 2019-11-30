import logging

from fastapi import Header

from common.controller import get, router, post, put
from request.user import User, UserLogin, UserUpdate, UserForget, UserJoin, SendMessage
from service.user import UserService

LOGGER = logging.getLogger(__name__)


@router('/users', tags=['user'])
class UserController:

    def __init__(self, user_service: UserService) -> None:
        super().__init__()

        self.user_service = user_service
        LOGGER.debug('UserController Created')

    @get('/?')
    def get_user(self, ac_token: str = Header(None, min_length=50, max_length=50, convert_underscores=False)):
        return self.user_service.get_user(ac_token)

    @post('/?')
    def add_user(self, user: User):
        return self.user_service.add_user(user)

    @put('/?')
    def update_user(self, user: UserUpdate,
                    ac_token: str = Header(None, min_length=50, max_length=50, convert_underscores=False)):
        return self.user_service.update_user(ac_token, user)

    @post('/login')
    def user_login(self, user_login: UserLogin):
        return self.user_service.user_login(user_login)

    @post('/logout')
    def user_logout(self, ac_token: str = Header(None, min_length=50, max_length=50, convert_underscores=False)):
        return self.user_service.user_logout(ac_token)

    @post('/refresh')
    def refresh_user(self, rf_token: str = Header(None, min_length=50, max_length=50, convert_underscores=False)):
        return self.user_service.refresh_user(rf_token)

    @post('/forget')
    def user_forget(self, user_forget: UserForget):
        return self.user_service.user_forget(user_forget)

    @post('/join')
    def join_class(self, data: UserJoin,
                   ac_token: str = Header(None, min_length=50, max_length=50, convert_underscores=False)):
        return self.user_service.user_join_class(data, ac_token)

    @post('/conversations/send-message')
    def send_message(self, message: SendMessage,
                     ac_token: str = Header(None, min_length=50, max_length=50, convert_underscores=False)):
        return self.user_service.send_message(message, ac_token)

    @get('/conversations')
    def list_conversation(self, ac_token: str = Header(None, min_length=50, max_length=50, convert_underscores=False)):
        return self.user_service.list_conversation(ac_token)

    @get('/conversations/{id}')
    def get_conversation(self, id: int,
                         ac_token: str = Header(None, min_length=50, max_length=50, convert_underscores=False)):
        return self.user_service.get_conversation_info(id, ac_token)
