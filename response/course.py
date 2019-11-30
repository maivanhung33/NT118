from dataclasses import dataclass


@dataclass
class ClassInfo:
    id: int
    uuid:str
    classCode: str
    classKey:str
    courseName: str
    lecturer: str
    lecturerId: int
    classSize: int
    faculty: str
    quantity: int
    members: list
    startAt: int
    expireAt: int
    type: str

    @staticmethod
    def course_info(course: dict):
        return ClassInfo(id=course['id'],
                         uuid=course['uuid'],
                         classCode=course['classCode'],
                         classKey=course['__rawClassKey'],
                         courseName=course['courseName'],
                         lecturer=course['lecturer'],
                         lecturerId=course['lecturerId'],
                         classSize=course['classSize'],
                         faculty=course['faculty'],
                         quantity=course['quantity'],
                         members=course['members'],
                         startAt=course['startAt'],
                         expireAt=course['expireAt'],
                         type=course['type'])


@dataclass
class CourseList:
    count: int
    courses: list

    @staticmethod
    def course_list(list_course: list):
        return CourseList(count=len(list_course),
                          courses=list_course)


@dataclass
class RollCallInfo:
    id: int
    classId: int
    startAt: int
    expireAt: int
    mac: str
    location: dict
    total: int
    count: int

    @staticmethod
    def roll_call_info(roll_call: dict):
        return RollCallInfo(id=roll_call['id'],
                            classId=roll_call['classId'],
                            startAt=roll_call['startAt'],
                            expireAt=roll_call['expireAt'],
                            mac=roll_call['mac'],
                            location=dict(lat=roll_call['lat'], long=roll_call['long']),
                            total=roll_call['total'],
                            count=roll_call['count'])


@dataclass
class RollCallList:
    count: int
    rollCalls: list

    @staticmethod
    def roll_call_list(roll_call_list: list):
        return RollCallList(count=len(roll_call_list),
                            rollCalls=roll_call_list)


@dataclass
class NotificationInfo:
    id: int
    classId: int
    title: str
    body: str
    createdAt: int
    totalSeen: int
    listSeen: list

    @staticmethod
    def notification(data: dict):
        return NotificationInfo(id=data['id'],
                                classId=data['classId'],
                                title=data['title'],
                                body=data['body'],
                                createdAt=data['createdAt'],
                                totalSeen=data['totalSeen'],
                                listSeen=data['listSeen'])


@dataclass
class NotificationList:
    count: int
    notifications: list

    @staticmethod
    def list_notification(data: list):
        return NotificationList(count=len(data),
                                notifications=data)
