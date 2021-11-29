from data import db_session
from logging.config import dictConfig
from fastapi import FastAPI
from is_absent_api import api_router
import json

with open('log_config.json', 'r') as f:
    dictConfig(json.load(f))


app = FastAPI()
app.include_router(api_router)
db_session.global_init('data/is_absent.sqlite')  # Подключение к БД
