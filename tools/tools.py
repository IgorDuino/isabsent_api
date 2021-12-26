import random

from data.student import Student
from data.teacher import Teacher
from fuzzywuzzy import process


def generate_random_code() -> str:
    """Function that generate random code for teachers or students """
    etalon = list('qwertyuiopadfghjklzxcvbnm1234567890QWERTYUIOPASDFGHJKLZZXCVBNM')
    random.shuffle(etalon)
    return ''.join(etalon[:10])


def generate_unique_code(db_sess) -> str:
    """Function that generate random code until it be unique"""
    code = generate_random_code()
    while not (db_sess.query(Teacher).filter(Teacher.code == code).first() is None and
               db_sess.query(Student).filter(Student.code == code).first() is None):
        code = generate_random_code()
    return code


def find_student(student_list: list, key: str) -> list:
    """
    Function that find 5 most similar in name students from list

    students_list: list - list of students used for search
    key: str - search key
    """
    student_name_list = list(map(lambda x: x[0], student_list))
    find = process.extract(key, student_name_list)
    find = list(map(lambda x: student_list[student_name_list.index(x[0])][1], find))
    return find