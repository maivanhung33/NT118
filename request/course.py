from pydantic import BaseModel


class Class(BaseModel):
    courseName: str
    classCode: str
    classKey: str
    classSize: int
    faculty: str
    startAt: int
    expireAt: int
    type: str


class UpdateClass(BaseModel):
    courseName: str = None
    classCode: str = None
    classKey: str = None
    classSize: int = None
    lecturer: str = None
    faculty: str = None
    startAt: int = None
    expireAt: int = None
    type: str = None


class RollCall(BaseModel):
    startAt: int
    expireAt: int
    mac: str
    lat: float
    long: float


class UpdateRollCall(BaseModel):
    startAt: int = None
    expireAt: int = None
    mac: str = None
    lat: float = None
    long: float = None


class Checkin(BaseModel):
    mac: str = None
    lat: float = None
    long: float = None


class Notification(BaseModel):
    title: str
    body: str
