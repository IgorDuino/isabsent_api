from pydantic import BaseModel
from typing import Optional, List


class OkResponse(BaseModel):
    msg: str


class BadResponse(BaseModel):
    error_msg: str


class TeacherTgAuth(BaseModel):
    code: str
    tg_user_id: int


class TeacherCodeTgUserId(BaseModel):
    code: Optional[str]
    tg_user_id: Optional[int]


class Teacher(BaseModel):
    name: str
    surname: str
    patronymic: str
    class_name: str
    school_name: str
    tg_user_id: Optional[int]


class StudentTgAuth(BaseModel):
    code: str
    tg_user_id: int


class StudentCodeTgUserId(BaseModel):
    code: Optional[str]
    tg_user_id: Optional[int]


class StudentAbsent(BaseModel):
    code: Optional[str]
    tg_user_id: Optional[int]
    date: str
    reason: str
    file: Optional[bytes]


class StudentAbsentList(BaseModel):
    absents: List[StudentAbsent]


class Student(BaseModel):
    name: str
    surname: str
    patronymic: str
    class_name: str
    school_name: str
    tg_user_id: Optional[int]
