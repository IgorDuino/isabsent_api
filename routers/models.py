from pydantic import BaseModel
from typing import Optional, List


class OkResponse(BaseModel):
    msg: str


class BadResponse(BaseModel):
    error_msg: str


class TgAuth(BaseModel):
    code: str
    tg_user_id: int


class CodeTgUserId(BaseModel):
    code: Optional[str]
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


class TeacherPatch(BaseModel):
    new_name: Optional[str]
    new_surname: Optional[str]
    new_patronymic: Optional[str]
    new_class_name: Optional[str]
    new_school_name: Optional[str]


class StudentTeacher(BaseModel):
    name: str
    surname: str
    patronymic: str
    class_name: str
    school_name: str
    type: str
    tg_user_id: Optional[int]


class Absent(BaseModel):
    date: str
    reason: str
    file: Optional[bytes]


class AbsentGet(BaseModel):
    code: str
    date: str
    reason: str
    file: Optional[bytes]


class AbsentGetList(BaseModel):
    absents: List[AbsentGet]


class AbsentPatch(BaseModel):
    new_date: str
    new_reason: str
    new_file: Optional[bytes]


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


class StudentPatch(BaseModel):
    new_name: Optional[str]
    new_surname: Optional[str]
    new_patronymic: Optional[str]
    new_class_name: Optional[str]
    new_school_name: Optional[str]


class School(BaseModel):
    school_name: str
    link: str


class SchoolPatch(BaseModel):
    new_name: Optional[str]
    new_link: Optional[str]


class SchoolList(BaseModel):
    schools: List[School]


class FindByNameResponse(BaseModel):
    students: List[StudentGet]
