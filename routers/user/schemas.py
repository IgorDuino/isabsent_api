from pydantic import BaseModel
from typing import Optional, List


class User(BaseModel):
    email: str
    login: str
    password: str
    info: Optional[str]


class UserGet(BaseModel):
    email: str
    login: str
    info: Optional[str]


class UserPatch(BaseModel):
    new_password: Optional[str]
    new_email: Optional[str]
    new_login: Optional[str]
    new_info: Optional[str]
