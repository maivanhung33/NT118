import logging

from fastapi import Header

from request.course import Class, UpdateClass, RollCall, UpdateRollCall, Checkin, Notification
from common.controller import router, get, post, put, delete
from service.course import ClassService

LOGGER = logging.getLogger(__name__)


@router('/courses', tags=['courses'])
class CourseController:

    def __init__(self, course_service: ClassService) -> None:
        super().__init__()
        self.course_service = course_service
        LOGGER.debug('CourseController Created')

    @get('/?')
    def list_course(self, ac_token: str = Header(None, min_length=50, max_length=50, convert_underscores=False)):
        return self.course_service.list_user_course(ac_token)

    @post('/?')
    def add_course(self, course: Class,
                   ac_token: str = Header(None, min_length=50, max_length=50, convert_underscores=False)):
        return self.course_service.add_course(ac_token, course)

    @get('/{course_id}')
    def get_course(self, course_id: int):
        return self.course_service.get_course(course_id)

    @put('/{course_id}')
    def update_course(self, course_id: int, update_course: UpdateClass,
                      ac_token: str = Header(None, min_length=50, max_length=50, convert_underscores=False)):
        return self.course_service.update_course(course_id, update_course, ac_token)

    @delete('/{course_id}')
    def delete_course(self, course_id: int,
                      ac_token: str = Header(None, min_length=50, max_length=50, convert_underscores=False)):
        return self.course_service.delete_course(course_id, ac_token)

    @get('/{course_id}/roll-calls')
    def list_roll_call(self, course_id: int,
                       ac_token: str = Header(None, min_length=50, max_length=50, convert_underscores=False)):
        return self.course_service.list_roll_call(course_id, ac_token)

    @post('/{course_id}/roll-call')
    def add_roll_call(self, course_id: int, roll_call: RollCall,
                      ac_token: str = Header(None, min_length=50, max_length=50, convert_underscores=False)):
        return self.course_service.add_roll_call(course_id, roll_call, ac_token)

    @get('/{course_id}/roll-calls/{roll_call_id}')
    def get_roll_call(self, course_id: int, roll_call_id: int):
        return self.course_service.get_roll_call(course_id, roll_call_id)

    @put('/{course_id}/roll-call/{roll_call_id}')
    def update_roll_call(self, course_id: int, roll_call_id: int, roll_call: UpdateRollCall,
                         ac_token: str = Header(None, min_length=50, max_length=50, convert_underscores=False)):
        return self.course_service.update_roll_call(course_id, roll_call_id, roll_call, ac_token)

    @post('/{course_id}/roll-call/{roll_call_id}/checkin')
    def checkin(self, course_id: int, roll_call_id: int, checkin: Checkin,
                ac_token: str = Header(None, min_length=50, max_length=50, convert_underscores=False)):
        return self.course_service.checkin(course_id, roll_call_id, checkin, ac_token)

    @get('/{course_id}/roll-call/{roll_call_id}/checkin')
    def check_checkin(self, course_id: int, roll_call_id: int,
                      ac_token: str = Header(None, min_length=50, max_length=50, convert_underscores=False)):
        return self.course_service.check_checkin(course_id, roll_call_id, ac_token)

    @get('/{course_id}/roll-call/{roll_call_id}/list-check')
    def list_checkin(self, course_id: int, roll_call_id: int):
        return self.course_service.list_checkin(course_id, roll_call_id)

    @get('/{id}/notifications')
    def list_notification(self, id: int,
                          ac_token: str = Header(None, min_length=50, max_length=50, convert_underscores=False)):
        return self.course_service.list_notification(id, ac_token)

    @get('/notifications/{id}')
    def get_notification(self, id: int,
                         ac_token: str = Header(None, min_length=50, max_length=50, convert_underscores=False)):
        return self.course_service.get_notification(id, ac_token)

    @post('/{id}/notifications')
    def add_notification(self,id:int, notification: Notification,
                         ac_token: str = Header(None, min_length=50, max_length=50, convert_underscores=False)):
        return self.course_service.add_notification(id,notification, ac_token)
