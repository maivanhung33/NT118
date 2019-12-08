import random
import string
import uuid

import hashlib
import pytz
from injector import singleton, inject
from pymongo import MongoClient, errors
from starlette.config import Config
from starlette.responses import JSONResponse
from response.user import InfoUser
from request.user import User, UserUpdate, UserLogin, UserForget, UserJoin, SendMessage
from datetime import datetime, timedelta
from common.exception import NotFoundException


@inject
@singleton
class UserService:

    def __init__(self, mongo: MongoClient, config: Config) -> None:
        super().__init__()
        self.mongo: MongoClient = mongo
        self.user = config('COL_USER', cast=str, default='user')
        self.courses = config('COL_COURSES', cast=str, default='courses')
        self.roll_call = config('COL_ROLL_CALL', cast=str, default='roll_call')
        self.checkin_data = config('COL_CHECKIN_DATA', cast=str, default='checkin_data')
        self.token = config('COL_TOKEN', cast=str, default='token')
        self.rf_token = config('COL_RF_TOKEN', cast=str, default='rf_token')
        self.key = config('KEY', cast=str, default='')
        self.conversation = config('CONVERSATION', cast=str, default='conversation')
        self.message = config('MESSAGE', cast=str, default='message')

    @staticmethod
    def check_day(last: datetime, now: datetime):
        if last.year == now.year:
            if last.month == now.month:
                if last.day == now.day:
                    return True
        return False

    def check_ac_token(self, ac_token):
        try:
            token = list(self.mongo[self.token].find({'key': ac_token}, {'_id': 0}).limit(1))[0]
            if self.check_day(token['__expiredAt'], datetime.now()):
                self.mongo[self.token].update_one({'key': ac_token}, {
                    '$set': {'__expiredAt': datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")) + timedelta(7)}})
            return token['userUuid']
        except IndexError:
            return None

    def check_rf_token(self, rf_token):
        try:
            user = list(self.mongo[self.rf_token].find({'key': rf_token}, {'_id': 0}).limit(1))[0]
            return user['userUuid']
        except IndexError:
            return None

    def get_ac_token(self, user_name, password):
        try:
            user = list(self.mongo[self.user].find({'userName': user_name, 'password': password},
                                                   {'_id': 0}).limit(1))[0]
            try:
                token = list(self.mongo[self.token].find({'userUuid': user['uuid']}, {'_id': 0}).limit(1))[0]
                return dict(userUuid=user['uuid'], key=token['key'])
            except IndexError:
                return dict(userUuid=user['uuid'], key=None)
        except IndexError:
            return False

    def get_user(self, ac_token):
        if ac_token is None:
            raise NotFoundException(404, "Token not found")
        user_uuid = self.check_ac_token(ac_token)
        if user_uuid is None:
            raise NotFoundException(404, "User not found")
        user = list(self.mongo[self.user].find({'uuid': user_uuid}, {'_id': 0}).limit(1))[0]
        return InfoUser.info_user(user)

    def update_user(self, ac_token, user: UserUpdate):
        if ac_token is None:
            return JSONResponse(status_code=400, content={'message': 'token is missed'})
        user_uuid = self.check_ac_token(ac_token)
        if user_uuid is None:
            return JSONResponse(status_code=401, content={'message': 'Invalid Token'})
        value = dict(user)
        for k, v in value.items():
            if value[k] is None:
                return JSONResponse(status_code=400, content={'message': 'Mục {} không được để trống'.format(k)})
        value['answer'] = hashlib.md5(value['answer'].encode()).hexdigest()
        query = {'uuid': user_uuid}
        self.mongo[self.user].update_one(query, {'$set': value})
        return JSONResponse(status_code=400, content={'message': 'Cập nhật thành công'})

    def user_login(self, user_login: UserLogin):
        data = self.get_ac_token(user_login.userName, hashlib.md5(user_login.password.encode()).hexdigest())
        if not data:
            return JSONResponse(status_code=401, content={'message': 'Sai tên đăng nhập hoặc mật khẩu'})
        if data['key'] is not None:
            # letters = string.ascii_lowercase
            # rf_token = ''.join(random.choice(letters) for i in range(50))
            # self.mongo[self.rf_token].update({'userId': data['userId']}, {
            #     '$set': {'userId': data['userId'], 'key': rf_token,
            #              '__expiredAt': datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))}}, True)
            # return JSONResponse(status_code=201, content={
            #     'message': 'Có một thiết bị khác đang đăng nhập. Bạn có muốn đăng xuất khỏi thiết bị đó ?'},
            #                     headers={'rf_token': rf_token})
            return JSONResponse(status_code=200, content={'message': 'Đăng nhập thành công'},
                                headers={'token': data['key']})

        letters = string.ascii_letters
        ac_token = ''.join(random.choice(letters) for i in range(50))
        self.mongo[self.token].insert(
            {'userUuid': data['userUuid'], 'key': ac_token,
             '__expiredAt': datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")) + timedelta(7)})
        return JSONResponse(status_code=200, content={'message': 'Đăng nhập thành công'}, headers={'token': ac_token})

    def add_user(self, user: User):
        value = dict(user)
        for k, v in value.items():
            if value[k] is None:
                return JSONResponse(status_code=400, content={'message': 'Mục {} không được để trống'.format(k)})
        try:
            user_id = list(self.mongo[self.user].find({}).sort('id', -1).limit(1))[0]['id'] + 1
        except IndexError:
            user_id = 1
        value['id'] = user_id
        value['uuid'] = uuid.uuid4().__str__()
        value['courses'] = []
        value['password'] = hashlib.md5(value['password'].encode()).hexdigest()
        value['answer'] = hashlib.md5(value['answer'].encode()).hexdigest()
        value['conversations'] = list()
        try:
            self.mongo[self.user].insert(value)
            return JSONResponse(status_code=200, content={'message': 'Đăng ký thành công'})
        except errors.DuplicateKeyError:
            return JSONResponse(status_code=400, content={'message': 'Tài khoản đã tồn tại'})

    def user_logout(self, ac_token):
        if ac_token is None:
            return JSONResponse(status_code=400, content={'message': 'token is missed'})
        token = self.check_ac_token(ac_token)
        if token is None:
            return JSONResponse(status_code=401, content={'message': 'Invalid Token'})
        self.mongo[self.token].delete_one({'key': ac_token})
        return JSONResponse(status_code=200, content={'message': 'Đã log out'})

    def refresh_user(self, rf_token):
        if rf_token is None:
            return JSONResponse(status_code=400, content={'message': 'token is missed'})
        user_uuid = self.check_rf_token(rf_token)
        if user_uuid is None:
            return JSONResponse(status_code=400)
        self.mongo[self.rf_token].delete_many({'key': rf_token})
        self.mongo[self.token].delete_many({'userUuid': user_uuid})
        return JSONResponse(status_code=200, content={'message': 'Đã đăng xuất khỏi tất các thiết bị'})

    def user_forget(self, user_forget: UserForget):
        temp = user_forget
        value = dict(temp)
        for k, v in value.items():
            if value[k] is None:
                return JSONResponse(status_code=400, content={'message': 'Mục {} không được để trống'.format(k)})
        try:
            user = list(self.mongo[self.user].find({'userName': user_forget.userName}, {'_id': 0}).limit(1))[0]

            if user['questionRecovery'] != user_forget.questionRecovery:
                return JSONResponse(status_code=400, content={'message': 'Sai Câu Hỏi'})
            if user['answer'] != hashlib.md5(user_forget.answer.encode()).hexdigest():
                return JSONResponse(status_code=400, content={'message': 'Câu trả lời không chính xác !'})
            self.mongo[self.user].update({'id': user['id']},
                                         {'$set': {
                                             'password': hashlib.md5(user_forget.newPassword.encode()).hexdigest()}})
            self.mongo[self.rf_token].delete_many({'userUuid': user['uuid']})
            self.mongo[self.token].delete_many({'userUuid': user['uuid']})
            return JSONResponse(status_code=200, content={'message': 'Cập nhật thành công !'})
        except IndexError:
            return JSONResponse(status_code=404, content={'message': 'Not Found User'})

    def user_join_class(self, data: UserJoin, ac_token: str):
        user = self.get_user(ac_token)
        try:
            course = list(self.mongo[self.courses].find(
                {'classCode': data.classCode, 'classKey': hashlib.md5(data.classKey.encode()).hexdigest()},
                {'_id': 0}))[0]
            user_courses = user.courses
            if course['uuid'] in user_courses:
                return JSONResponse(status_code=422, content={'message': "Đã tham gia"})

            user_courses.append(course['uuid'])
            self.mongo[self.user].update_one({'id': user.id}, {'$set': {'courses': user_courses}})

            members = course['members']
            member = dict(id=user.id, name=user.name)
            members.append(member)
            self.mongo[self.courses].update_one({'id': course['id']}, {'$set': {'members': members,
                                                                                'quantity': course['quantity'] + 1}})

            return JSONResponse(status_code=200, content={'message': 'Thành công'})
        except IndexError:
            return JSONResponse(status_code=422, content={'message': "Sai Key hoặc mã lớp"})

    def send_message(self, data: SendMessage, ac_token: str):
        user_info = self.get_user(ac_token)
        if data.userNameReceive is None and data.userUuidReceive is None:
            return JSONResponse(status_code=400,
                                content={'message': 'Just userNameReceive or userUuidReceive need field'})
        try:
            if data.userUuidReceive is None:
                receiver = list(self.mongo[self.user].find({'userName': data.userNameReceive}, {'_id': 0}))[0]
            else:
                receiver = list(self.mongo[self.user].find({'uuid': data.userUuidReceive}, {'_id': 0}))[0]
        except IndexError:
            raise NotFoundException(404, 'Không tìm thấy người nhận')
        query = {'senderUuid': {'$in': [user_info.uuid, receiver['uuid']]},
                 'receiverUuid': {'$in': [user_info.uuid, receiver['uuid']]}}
        try:
            conversation = list(self.mongo[self.conversation].find(query, {'_id': 0}).limit(1))[0]
        except IndexError:
            conversation = None
        if conversation is None:
            try:
                con_id = list(self.mongo[self.conversation].find({}).sort('id', -1).limit(1))[0]['id'] + 1
            except IndexError:
                con_id = 1
            conversation = dict(id=con_id,
                                senderUuid=user_info.uuid,
                                senderName=user_info.name,
                                receiverUuid=receiver['uuid'],
                                receiverName=receiver['name'],
                                totalMessage=0,
                                createdAt=int(datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).timestamp()),
                                lastActive=int(datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).timestamp()))
            self.mongo[self.conversation].insert(conversation)
        message = dict(conversationId=conversation['id'],
                       senderUuid=user_info.uuid,
                       receiverUuid=receiver['uuid'],
                       receiverName=receiver['name'],
                       content=data.content,
                       sendAt=int(datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).timestamp()),
                       isSeen=False)
        self.mongo[self.message].insert(message)
        self.mongo[self.conversation].update_one({'id': conversation['id']},
                                                 {'$set': {'lastActive': message['sendAt'],
                                                           'totalMessage': conversation['totalMessage'] + 1}})

        self.mongo[self.message].find_and_modify(query={'conversationId': conversation['id'],
                                                        'receiverUuid': user_info.uuid, 'isSeen': False},
                                                 update={'$set': {'isSeen': True}})
        response = list(self.mongo[self.message].find({'conversationId': conversation['id']},
                                                      {'_id': 0, 'senderUuid': 1, 'content': 1, 'sendAt': 1})
                        .sort('sendAt', -1))
        return response

    def list_conversation(self, ac_token):
        user_info = self.get_user(ac_token)
        query_1 = {'senderUuid': user_info.uuid}
        query_2 = {'receiverUuid': user_info.uuid}
        list_1 = list(self.mongo[self.conversation].find(query_1, {'_id': 0}).sort('lastActive', -1))
        list_2 = list(self.mongo[self.conversation].find(query_2, {'_id': 0}).sort('lastActive', -1))
        conversations = list_1 + list_2
        conversations.sort(key=lambda x: x['lastActive'], reverse=True)
        response = dict(total=0,
                        conversations=list())
        for con in conversations:
            last_message = list(self.mongo[self.message].find({'conversationId': con['id']}, {'_id': 0})
                                .sort('sendAt', -1).limit(1))[0]
            response['conversations'].append(dict(conversationId=con['id'],
                                                  partnerUuid=con['senderUuid']
                                                  if user_info.uuid != con['senderUuid'] else con['receiverUuid'],
                                                  partnerName=con['senderName']
                                                  if user_info.uuid != con['senderUuid'] else con['receiverName'],
                                                  lastActive=last_message['sendAt'],
                                                  last_message=last_message['content'],
                                                  isSeenLastMessage=last_message['isSeen']
                                                  if user_info.uuid != last_message['senderUuid'] else True))
        response['total'] = len(response['conversations'])
        return response

    def get_conversation_info(self, conversation_id: int, ac_token):
        try:
            conversation = list(self.mongo[self.conversation].find({'id': conversation_id}, {'_id': 0})
                                .limit(1))[0]
        except IndexError:
            raise NotFoundException(404, 'Conversation Not Found')

        user_info = self.get_user(ac_token)
        if conversation['senderUuid'] != user_info.uuid and conversation['receiverUuid'] != user_info.uuid:
            return JSONResponse(status_code=400, content={'message': 'Không có quyền truy cập'})

        self.mongo[self.message].find_and_modify(query={'conversationId': conversation_id,
                                                        'receiverUuid': user_info.uuid, 'isSeen': False},
                                                 update={'$set': {'isSeen': True}})
        response = dict(userUuid=user_info.uuid,
                        messages=list())
        response['messages'] = list(self.mongo[self.message].find({'conversationId': conversation_id},
                                                                  {'_id': 0, 'senderUuid': 1, 'content': 1,
                                                                   'sendAt': 1})
                                    .sort('sendAt', -1))
        return response
