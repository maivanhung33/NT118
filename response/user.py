from dataclasses import dataclass


@dataclass
class InfoUser:
    id: int
    uuid: str
    name: str
    birth: int
    sex: str
    phone: str
    mail: str
    className: str
    major: str
    faculty: str
    accountType: int
    courses: list

    @staticmethod
    def info_user(user: dict):
        return InfoUser(id=user['id'],
                        uuid=user['uuid'],
                        name=user['name'],
                        birth=user['birth'],
                        sex=user['sex'],
                        phone=user['phone'],
                        mail=user['mail'],
                        className=user['className'],
                        major=user['major'],
                        faculty=user['faculty'],
                        accountType=user['accountType'],
                        courses=user['courses'])
