import uuid
import hashlib
import pytz

from injector import singleton, inject
from pymongo import MongoClient, errors, ReturnDocument
from starlette.config import Config
from starlette.responses import JSONResponse
from response.course import ClassInfo, CourseList, RollCallInfo, RollCallList, NotificationList, NotificationInfo
from request.course import Class, UpdateClass, RollCall, UpdateRollCall, Checkin, Notification
from service.user import UserService
from common.exception import NotFoundException
from datetime import datetime, timedelta
from geopy import distance


@inject
@singleton
class ClassService:

    def __init__(self, mongo: MongoClient, config: Config, user: UserService) -> None:
        super().__init__()
        self.user_service: UserService = user
        self.mongo: MongoClient = mongo
        self.user = config('COL_USER', cast=str, default='user')
        self.courses = config('COL_COURSES', cast=str, default='courses')
        self.roll_call = config('COL_ROLL_CALL', cast=str, default='roll_call')
        self.checkin_data = config('COL_CHECKIN_DATA', cast=str, default='checkin_data')
        self.token = config('COL_TOKEN', cast=str, default='token')
        self.rf_token = config('COL_RF_TOKEN', cast=str, default='rf_token')
        self.checkin_user = config('CHECKIN_USER', cast=str, default='checkin_user')
        self.notification = config('NOTIFICATION', cast=str, default='notification')

    def get_course(self, class_id: int):
        try:
            course = list(self.mongo[self.courses].find({'id': class_id}, {'_id': 0}).limit(1))[0]
            return ClassInfo.course_info(course)
        except IndexError:
            raise NotFoundException(404, "course not found")

    def get_roll_call(self, class_id: int, roll_call_id: int):
        try:
            roll_call = list(self.mongo[self.roll_call].find({'classId': class_id, 'id': roll_call_id},
                                                             {'_id': 0, 'uuid': 0}).limit(1))[0]
            return RollCallInfo.roll_call_info(roll_call)
        except IndexError:
            raise NotFoundException(404, "roll call not found")

    def list_user_course(self, ac_token):
        user = self.user_service.get_user(ac_token)
        courses = list()
        for item in user.courses:
            try:
                course = list(self.mongo[self.courses].find({'uuid': item},
                                                            {'_id': 0, 'uuid': 0, 'lecturerId': 0,
                                                             '__expireAt': 0, 'classKey': 0, '__rawClassKey': 0})
                              .limit(1))[0]
                courses.append(course)
            except IndexError:
                continue
        return CourseList.course_list(courses)

    def list_roll_call(self, class_id: int, ac_token: str):
        roll_calls = list(
            self.mongo[self.roll_call].find({'classId': class_id}, {'_id': 0, 'uuid': 0, '__expireAt': 0}))
        for item in roll_calls:
            item['isCheckin'] = self.check_checkin(class_id, item['id'], ac_token)['check']
        return RollCallList.roll_call_list(roll_calls)

    def add_course(self, ac_token, course: Class):
        user = self.user_service.get_user(ac_token)
        if user.accountType != 2:
            return JSONResponse(status_code=403, content={'message': 'Not Permission'})
        try:
            course_id = list(self.mongo[self.courses].find({}).sort('id', -1).limit(1))[0]['id'] + 1
        except IndexError:
            course_id = 1
        data = dict(course)
        data['__rawClassKey'] = data['classKey']
        data['classKey'] = hashlib.md5(data['classKey'].encode()).hexdigest()
        data['uuid'] = uuid.uuid4().__str__()
        data['id'] = course_id
        data['lecturer'] = user.name
        data['lecturerId'] = user.id
        data['quantity'] = 0
        data['members'] = list()
        data['__expireAt'] = datetime.fromtimestamp(course.expireAt) + timedelta(30)
        try:
            self.mongo[self.courses].insert(data)
            user_courses = user.courses
            user_courses.append(data['uuid'])
            self.mongo[self.user].update_one({'id': user.id}, {'$set': {'courses': user_courses}})
            return ClassInfo.course_info(data)
        except errors.DuplicateKeyError:
            return JSONResponse(status_code=400, content={'message': 'Course đã tồn tại'})

    def add_roll_call(self, class_id: int, roll_call: RollCall, ac_token: str):
        course = self.get_course(class_id)
        user = self.user_service.get_user(ac_token)
        if course.lecturerId != user.id:
            return JSONResponse(status_code=403, content={'message': 'Not Permission'})
        data = dict(roll_call)
        data['classId'] = course.id
        try:
            id = list(self.mongo[self.roll_call].find({}).sort('id', -1).limit(1))[0]['id'] + 1
        except IndexError:
            id = 1
        data['id'] = id
        data['uuid'] = uuid.uuid4().__str__()
        data['total'] = course.classSize
        data['count'] = 0
        data['__expireAt'] = datetime.fromtimestamp(course.expireAt) + timedelta(30)
        try:
            self.mongo[self.roll_call].insert(data)
            return RollCallInfo.roll_call_info(data)
        except IndexError:
            return RollCallInfo.roll_call_info(data)

    def update_course(self, class_id: int, update_course: UpdateClass, ac_token):
        course = self.get_course(class_id)
        user = self.user_service.get_user(ac_token)
        if user.id != course.lecturerId:
            return JSONResponse(status_code=403, content={'message': 'Not Permission'})
        data = dict(update_course)
        if 'classKey' in data.keys():
            data['classKey'] = hashlib.md5(data['classKey'].encode()).hexdigest()
        query = {'id': class_id}
        course = self.mongo[self.courses].find_one_and_update(query, {'$set': data},
                                                              return_document=ReturnDocument.AFTER)
        return ClassInfo.course_info(course)

    def update_roll_call(self, class_id: int, roll_call_id: int, update_roll_call: UpdateRollCall, ac_token: str):
        course = self.get_course(class_id)
        user = self.user_service.get_user(ac_token)
        roll_call = self.get_roll_call(class_id, roll_call_id)
        if user.id != course.lecturerId:
            return JSONResponse(status_code=403, content={'message': 'Not Permission'})
        data = dict(update_roll_call)
        query = {'id': roll_call_id}
        response = self.mongo[self.roll_call].find_one_and_update(query, {'$set': data}, {'_id': 0},
                                                                  return_document=ReturnDocument.AFTER)
        return RollCallInfo.roll_call_info(response)

    def delete_course(self, class_id: int, ac_token):
        course = self.get_course(class_id)
        user = self.user_service.get_user(ac_token)
        if user.id != course.lecturerId:
            return JSONResponse(status_code=403, content={'message': 'Not Permission'})
        self.mongo[self.courses].delete_one({'id': class_id})
        self.mongo[self.notification].delete_many({'classId': class_id})
        self.mongo[self.roll_call].delete_many({'classId': class_id})
        self.mongo[self.checkin_user].delete_many({'classId': class_id})

    def checkin(self, class_id: int, roll_call_id: int, checkin: Checkin, ac_token: str):
        course = self.get_course(class_id)
        roll_call = self.get_roll_call(class_id, roll_call_id)
        user = self.user_service.get_user(ac_token)
        if self.check_checkin(class_id, roll_call_id, ac_token)['check']:
            return JSONResponse(status_code=400, content={'message': 'Bạn đã điểm danh rồi'})
        has_join = False
        course_uuid = list(self.mongo[self.courses].find({'id': class_id}, {'_id': 0}).limit(1))[0]['uuid']
        for item in user.courses:
            if item == course_uuid:
                has_join = True
                break
        if not has_join:
            return JSONResponse(status_code=400, content={'message': 'Bạn chưa tham gia lớp'})
        if datetime.timestamp(datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))) > roll_call.expireAt:
            return JSONResponse(status_code=400, content={'message': 'Buổi điểm danh đã kết thúc'})
        if datetime.timestamp(datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))) < roll_call.startAt:
            return JSONResponse(status_code=400, content={'message': 'Buổi điểm danh chưa bắt đầu'})
        response = dict(status=False,
                        mac=False,
                        location=False)
        if checkin.mac == roll_call.mac:
            response['mac'] = True
            org_loc = (roll_call.location['lat'], roll_call.location['long'])
            check_loc = (checkin.lat, checkin.long)
            if int(distance.distance(org_loc, check_loc).m) <= 30:
                response['location'] = True
                response['status'] = True
        for key in response.keys():
            if not response[key]:
                return JSONResponse(status_code=422, content=response)
        new_count = roll_call.count + 1
        self.mongo[self.roll_call].update_one({'id': roll_call.id}, {'$set': {'count': new_count}})
        checkin_user = dict(name=user.name,
                            userId=user.id,
                            classId=course.id,
                            rollCallId=roll_call.id,
                            checkAt=datetime.timestamp(datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))),
                            __expireAt=datetime.fromtimestamp(course.expireAt,
                                                              tz=pytz.timezone("Asia/Ho_Chi_Minh")) + timedelta(30))
        try:
            self.mongo[self.checkin_user].insert(checkin_user)
            return JSONResponse(status_code=200, content=response)
        except errors.DuplicateKeyError:
            return JSONResponse(status_code=200, content=response)

    def check_checkin(self, class_id: int, roll_call_id: int, ac_token: str):
        course = self.get_course(class_id)
        roll_call = self.get_roll_call(class_id, roll_call_id)
        user = self.user_service.get_user(ac_token)
        query = dict(userId=user.id,
                     classId=course.id,
                     rollCallId=roll_call.id)
        try:
            data = list(self.mongo[self.checkin_user].find(query, {'_id': 0}).limit(1))[0]
            return {'check': True}
        except IndexError:
            return {'check': False}

    def list_checkin(self, class_id: int, roll_call_id: int):
        course = self.get_course(class_id)
        roll_call = self.get_roll_call(class_id, roll_call_id)
        query = dict(classId=course.id,
                     rollCallId=roll_call.id)
        list_checkin = list(self.mongo[self.checkin_user].find(query, {'_id': 0, 'name': 1, 'checkAt': 1}))
        return dict(members=list_checkin,
                    total=roll_call.total,
                    count=roll_call.count)

    def add_notification(self, class_id: int, request: Notification, ac_token: str):
        user_info = self.user_service.get_user(ac_token)
        self.get_course(class_id)
        if user_info.accountType != 2:
            return JSONResponse(status_code=403, content={'message': 'Not Permission'})
        try:
            not_id = list(self.mongo[self.notification].find({}, {'_id': 0}).sort('id', -1).limit(1))[0]['id'] + 1
        except IndexError:
            not_id = 1
        notification = dict(request)
        notification['id'] = not_id
        notification['classId'] = class_id
        notification['createdAt'] = int(datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).timestamp())
        notification['totalSeen'] = 0
        notification['listSeen'] = list()
        try:
            self.mongo[self.notification].insert(notification)
            return NotificationInfo.notification(notification)
        except errors.DuplicateKeyError:
            return NotificationInfo.notification(notification)

    def list_notification(self, class_id: int, ac_token: str):
        user_info = self.user_service.get_user(ac_token)
        class_info = self.get_course(class_id)
        if class_info.uuid not in user_info.courses:
            return JSONResponse(status_code=400, content={'message': 'Bạn phải là thành viên của lớp'})
        notifications = list(self.mongo[self.notification].find({'classId': class_id}, {'_id': 0, 'body': 0}))

        seen_data = dict(userId=user_info.id, name=user_info.name)
        for item in notifications:
            item['isSeen'] = True
            if user_info.accountType == 2:
                continue
            if seen_data not in item['listSeen']:
                item['isSeen'] = False

        return NotificationList.list_notification(notifications)

    def get_notification(self, notification_id: int, ac_token: str):
        user_info = self.user_service.get_user(ac_token)
        try:
            notification_info = list(self.mongo[self.notification].find({'id': notification_id}, {'_id': 0}))[0]
        except IndexError:
            raise NotFoundException(404, 'Notification Not Found')
        class_info = self.get_course(notification_info['classId'])
        if class_info.uuid not in user_info.courses:
            return JSONResponse(status_code=400, content={'message': 'Bạn phải là thành viên của lớp'})

        if user_info.accountType == 1:
            seen_data = dict(userId=user_info.id, name=user_info.name)
            if seen_data not in notification_info['listSeen']:
                notification_info['listSeen'].append(seen_data)
                notification_info['totalSeen'] += 1
                self.mongo[self.notification].update({'id': notification_id},
                                                     {'$set': {'listSeen': notification_info['listSeen'],
                                                               'totalSeen': notification_info['totalSeen']}})

        return NotificationInfo.notification(notification_info)
