import random

from data.student import Student
from data.teacher import Teacher
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


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


def find_student(student_list: list, key: str) -> list:
    student_name_list = list(map(lambda x: x[0], student_list))
    find = process.extract(key, student_name_list)
    find = list(map(lambda x: student_list[student_name_list.index(x[0])][1], find))
    return find