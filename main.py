import is_absent_api

from flask import Flask
from data import db_session
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.FileHandler',
        'filename': 'app.log',
        'formatter': 'default',
        'mode': 'w'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__, )
app.config['SECRET_KEY'] = 'secret_key'


def main():
    db_session.global_init('data/is_absent.sqlite')  # Подключение к БД
    app.register_blueprint(is_absent_api.blueprint, url_prefix='/v1')  # Подключение api
    app.run(port=8080, host='localhost')  # Запуск сервера


if __name__ == '__main__':
    main()
