import requests
import uvicorn
import logging

from data import db_session
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from routers.auth_router import auth_router, token_check
from routers.teacher_router import teacher_router
from routers.student_router import student_router
from routers.school_router import school_router


logger = logging.getLogger("uvicorn")
logger.addHandler(logging.FileHandler("./logs/app.log"))

app = FastAPI()
app.include_router(auth_router, tags=["Auth"])
app.include_router(teacher_router, prefix="/v1", tags=["Teacher"], dependencies=[Depends(token_check)])
app.include_router(student_router, prefix="/v1", tags=["Student"], dependencies=[Depends(token_check)])
app.include_router(school_router, prefix="/v1", tags=["School"], dependencies=[Depends(token_check)])

db_session.global_init("data/is_absent.sqlite")