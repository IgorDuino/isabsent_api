import logging

from data import db_session
from fastapi import Depends, FastAPI

from routers.auth.auth import token_check
from routers.auth.auth_router import auth_router
from routers.teacher.teacher_router import teacher_router
from routers.student.student_router import student_router
from routers.school.school_router import school_router
from routers.user.user_router import user_router

from tools.settings import *


logger = logging.getLogger("uvicorn")
logger.addHandler(logging.FileHandler("./logs/app.log"))

app = FastAPI(**APP_SETTINGS)

app.include_router(auth_router, prefix="/v1", tags=["Auth"])
app.include_router(user_router, prefix='/v1', tags=['User'])
app.include_router(teacher_router, prefix="/v1", tags=["Teacher"], dependencies=[Depends(token_check)])
app.include_router(student_router, prefix="/v1", tags=["Student"], dependencies=[Depends(token_check)])
app.include_router(school_router, prefix="/v1", tags=["School"], dependencies=[Depends(token_check)])


db_session.global_init(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
