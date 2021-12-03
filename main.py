import uvicorn
import logging

from data import db_session
from fastapi import FastAPI
from routers.teacher_router import teacher_router
from routers.student_router import student_router
from routers.school_router import school_router


logger = logging.getLogger("uvicorn")
logger.addHandler(logging.FileHandler("app.log"))


app = FastAPI()
app.include_router(teacher_router, prefix='/v1', tags=['Teacher'])
app.include_router(student_router, prefix='/v1', tags=['Student'])
app.include_router(school_router, prefix='/v1', tags=['School'])
db_session.global_init('data/is_absent.sqlite')

if __name__ == "__main__":  # Подключение к БД
    uvicorn.run("main:app", host="localhost", port=5050, reload=True)