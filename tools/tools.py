import random

from data.student import Student
from data.teacher import Teacher


def generate_random_code():
    ETALON = list('qwertyuiopadfghjklzxcvbnm1234567890QWERTYUIOPASDFGHJKLZZXCVBNM')
    random.shuffle(ETALON)
    return ''.join(ETALON[:10])


def generate_unique_code(db_sess):
    code = generate_random_code()
    while not (db_sess.query(Teacher).filter(Teacher.code == code).first() is None and
               db_sess.query(Student).filter(Student.code == code).first() is None):
        code = generate_random_code()
    return code