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


class TeacherPost(BaseModel):
    name: str
    surname: str
    patronymic: str
    class_name: str


class TeacherListPost(BaseModel):
    school_name: str
    teachers: Optional[List[TeacherPost]]


class TeacherGet(BaseModel):
    name: str
    surname: str
    patronymic: str
    class_name: str
    school_name: str
    code: str
    tg_user_id: Optional[int]


class TeacherListGet(BaseModel):
    teachers: List[TeacherGet]


class StudentTeacher(BaseModel):
    name: str
    surname: str
    patronymic: str
    class_name: str
    school_name: str
    type: str
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


class StudentAbsentGet(BaseModel):
    date: str
    reason: str
    file: Optional[bytes]


class StudentAbsentList(BaseModel):
    absents: List[StudentAbsentGet]


class StudentPost(BaseModel):
    name: str
    surname: str
    patronymic: str
    class_name: str


class StudentListPost(BaseModel):
    school_name: str
    students: Optional[List[StudentPost]]


class StudentGet(BaseModel):
    name: str
    surname: str
    patronymic: str
    class_name: str
    school_name: str
    code: str
    tg_user_id: Optional[int]


class StudentListGet(BaseModel):
    students: List[StudentGet]


class Student(BaseModel):
    name: str
    surname: str
    patronymic: str
    class_name: str
    school_name: str
    tg_user_id: Optional[int]


class School(BaseModel):
    school_name: str
    link: str

class SchoolList(BaseModel):
    schools: List[School]


class SchoolGet(BaseModel):
    school_name: str


class Absent(BaseModel):
    date: str
    reason: str
    code: str
    file: Optional[bytes]


class AbsentList(BaseModel):
    absents: List[Absent]


class FindByCode(BaseModel):
    code: Optional[str]
    tg_user_id: Optional[int]


class FindByName(BaseModel):
    code: Optional[str]
    tg_user_id: Optional[int]
    name: str


class FindByNameResponse(BaseModel):
    students: List[StudentGet]


class TeacherAbsents(BaseModel):
    date: Optional[str]
    code: Optional[str]
    tg_user_id: Optional[int]