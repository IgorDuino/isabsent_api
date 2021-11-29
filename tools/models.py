from pydantic import BaseModel
from typing import Optional


class TeacherTgAuth(BaseModel):
    code: str
    tg_user_id: int


class TeacherPasswordGenerate(BaseModel):
    code: Optional[str] = ''
    tg_user_id: Optional[int] = -1


class Teacher(BaseModel):
    pass


class StudentTgAuth(BaseModel):
    code: str
    tg_user_id: int


class Student(BaseModel):
    pass