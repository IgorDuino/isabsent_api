import base64
import logging

from fastapi import APIRouter, Response, status
from tools.error_book import *
from data import db_session
from tools.settings import *
from data.student import Student
from data.teacher import Teacher
from data.school import School
from data.absent import Absent
from tools.tools import generate_unique_code
from google_spreadsheets.google_spread_sheets import GoogleSpreadSheetsApi
import tools.models as json_body


api_router= APIRouter()
google_spread_sheets = GoogleSpreadSheetsApi('google_spreadsheets/google_credentials.json')


# @api_router.route('/school', methods=['POST'])
# def school_post():
#     try:
#         data_json = flask.request.json
#         request_data_validate.school_post_validate(data_json)
#         db_sess = db_session.create_session()
#
#         school = db_sess.query(School).get(data_json['school_name'])
#         if school is not None:
#             raise SchoolDuplicateError(data_json['school_name'])
#
#         school = School(
#             name=data_json['school_name'],
#             link=data_json['link']
#         )
#         db_sess.add(school)
#         db_sess.commit()
#
#         return make_response('HTTP 200 OK', 200)
#     except (SchoolDuplicateError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
#         logging.warning(error)
#         return make_response('HTTP 400 Bad Request', 400)
#
#
# @api_router.route('school/teachers', methods=['POST', 'GET'])
# def teachers_post_get():
#     try:
#         db_sess = db_session.create_session()
#         data_json = flask.request.json
#         from_sheet_flag = False
#
#         if flask.request.method == 'POST':
#             request_data_validate.teachers_post_validate(data_json)
#
#             school_name = data_json['school_name']
#             school = db_sess.query(School).get(school_name)
#             if school is None:
#                 raise StudentNotFoundError(school_name)
#
#             if len(data_json['teachers']) == 0:
#                 data_json = google_spread_sheets.google_sheets_get_teachers(school.link, school_name)
#                 from_sheet_flag = True
#
#             teacher_list = []
#             teacher_code_list = []
#             for teacher_json in data_json['teachers']:
#                 request_data_validate.teacher_post_validate(teacher_json)
#
#                 code = generate_unique_code(db_sess, Teacher)
#
#                 teacher_list.append(Teacher(
#                     name=teacher_json['name'],
#                     surname=teacher_json['surname'],
#                     patronymic=teacher_json['patronymic'],
#                     class_name=teacher_json['class_name'],
#                     school_name=school_name,
#                     code=code
#                 ))
#
#                 teacher_code_list.append([code])
#
#             db_sess.add_all(teacher_list)
#             db_sess.commit()
#
#             if from_sheet_flag:
#                 link = school.link
#                 google_spread_sheets.google_sheets_teachers_codes(link, teacher_code_list)
#
#             return make_response('HTTP 200 OK', 200)
#
#         if flask.request.method == 'GET':
#             request_data_validate.teachers_get_validate(data_json)
#             school_name = data_json['school_name']
#
#             teacher_list = db_sess.query(Teacher).filter(Teacher.school_name == school_name).all()
#
#             teacher_dict_list = []
#             for teacher in teacher_list:
#                 teacher_dict = {
#                     'name': teacher.name,
#                     'surname': teacher.surname,
#                     'patronymic': teacher.patronymic,
#                     'class_name': teacher.class_name,
#                     'school_name': teacher.school_name,
#                     'code': teacher.code
#                 }
#
#                 if not (teacher.tg_user_id is None):
#                     teacher_dict['tg_user_id'] = teacher.tg_user_id
#
#                 teacher_dict_list.append(teacher_dict)
#
#             return make_response({"teachers": teacher_dict_list}, 200)
#     except (StudentNotFoundError, SchoolNotFoundError, RequestDataKeysError,
#             RequestDataMissedKeyError, RequestDataTypeError) as error:
#         logging.warning(error)
#         return make_response('HTTP 400 Bad Request', 400)
#
#
# @api_router.route('school/students', methods=['POST', 'GET'])
# def students_post_get():
#     try:
#         db_sess = db_session.create_session()
#         data_json = flask.request.json
#         from_sheet_flag = False
#
#         if flask.request.method == 'POST':
#             request_data_validate.students_post_validate(data_json)
#
#             school_name = data_json['school_name']
#             school = db_sess.query(School).get(school_name)
#             if school is None:
#                 raise SchoolNotFoundError(school_name)
#
#             if len(data_json['students']) == 0:
#                 data_json = google_spread_sheets.google_sheets_get_students(school.link, school_name)
#                 from_sheet_flag = True
#
#             student_list = []
#             student_code_list = []
#             for teacher_json in data_json['students']:
#                 request_data_validate.student_post_validate(teacher_json)
#
#                 code = generate_unique_code(db_sess, Teacher)
#
#                 student_list.append(Student(
#                     name=teacher_json['name'],
#                     surname=teacher_json['surname'],
#                     patronymic=teacher_json['patronymic'],
#                     class_name=teacher_json['class_name'],
#                     school_name=school_name,
#                     code=code
#                 ))
#
#                 student_code_list.append([code])
#
#             db_sess.add_all(student_list)
#             db_sess.commit()
#
#             if from_sheet_flag:
#                 link = school.link
#                 google_spread_sheets.google_sheets_students_codes(link, student_code_list)
#
#             return make_response('HTTP 200 OK', 200)
#
#         if flask.request.method == 'GET':
#             request_data_validate.students_get_validate(data_json)
#             school_name = data_json['school_name']
#
#             student_list = db_sess.query(Student).filter(Student.school_name == school_name).all()
#
#             student_dict_list = []
#             for student in student_list:
#                 student_dict = {
#                     'name': student.name,
#                     'surname': student.surname,
#                     'patronymic': student.patronymic,
#                     'class_name': student.class_name,
#                     'school_name': student.school_name,
#                     'code': student.code
#                 }
#
#                 if not (student.tg_user_id is None):
#                     student_dict['tg_user_id'] = student.tg_user_id
#
#                 student_dict_list.append(student_dict)
#
#             return make_response({"students": student_dict_list}, 200)
#     except (SchoolNotFoundError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
#         logging.warning(error)
#         return make_response('HTTP 400 Bad Request', 400)
#
#
# @api_router.route('school/absents', methods=['GET'])
# def absents_get():
#     try:
#         db_sess = db_session.create_session()
#         data_json = flask.request.json
#
#         request_data_validate.absents_get_validate(data_json)
#
#         school_name = data_json['school_name']
#         absents = []
#
#         students = db_sess.query(Student).filter(Student.school_name == school_name).all()
#         for student in students:
#             absents += student.absents
#
#         absent_json_list = []
#         for absent in absents:
#             student = absent.student
#             absent_json = {
#                 "date": absent.date,
#                 "reason": absent.reason,
#                 "code": student.code
#             }
#
#             if not (absent.file is None):
#                 absent_json['file'] = absent.file
#
#             absent_json_list.append(absent_json)
#
#         return make_response({"absents": absent_json_list}, 200)
#     except (RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
#         logging.warning(error)
#         return make_response('HTTP 400 Bad Request', 400)
