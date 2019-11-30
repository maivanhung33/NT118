from enum import Enum
from typing import Optional
from fastapi import Query
from pydantic import BaseModel


class Sex(str, Enum):
    male = 'male'
    female = 'female'


class User(BaseModel):
    userName: str = Query(None, max_length=30)
    password: str = Query(None, max_length=50)
    name: str = Query(None, max_length=30)
    birth: int = Query(None)
    sex: Optional[Sex]
    phone: str = Query(None, max_length=11)
    mail: str = Query(None)
    className: str = Query(None, max_length=10)
    major: str = Query(None, max_length=50)
    faculty: str = Query(None, max_length=50)
    accountType: int = Query(None)
    questionRecovery: str = Query(None, max_length=70)
    answer: str = Query(None, max_length=30)


class UserUpdate(BaseModel):
    name: str = Query(None, max_length=30)
    birth: int = Query(None)
    sex: Optional[Sex] = Query(None)
    phone: str = Query(None, max_length=11)
    mail: str = Query(None)
    className: str = Query(None, max_length=10)
    major: str = Query(None, max_length=50)
    faculty: str = Query(None, max_length=50)
    questionRecovery: str = Query(None, max_length=70)
    answer: str = Query(None, max_length=30)


class UserLogin(BaseModel):
    userName: str = Query(None, max_length=30)
    password: str = Query(None, max_length=50)


class UserForget(BaseModel):
    userName: str = Query(None, max_length=30)
    questionRecovery: str = Query(None, max_length=70)
    answer: str = Query(None, max_length=30)
    newPassword: str = Query(None, max_length=50)


class UserJoin(BaseModel):
    classCode: str
    classKey: str


class SendMessage(BaseModel):
    userNameReceive: str = None
    userUuidReceive: str = None
    content: str
