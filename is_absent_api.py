import flask
import logging

from flask import make_response
from tools.error_book import *
from data import db_session
from tools import request_data_validate
from settings import *
from data.student import Student
from data.teacher import Teacher
from data.school import School
from data.absent import Absent
from tools.tools import generate_unique_code


blueprint = flask.Blueprint(
    'sdo_parser_api',
    __name__,
)


@blueprint.route('/teacher/tg_auth', methods=['POST'])
def teacher_tg_auth():
    try:
        data_json = flask.request.json
        request_data_validate.teacher_tg_auth_validate(data_json)

        code = data_json['code']
        tg_id = data_json['tg_user_id']

        db_sess = db_session.create_session()

        teacher = db_sess.query(Teacher).filter(Teacher.code == code).first()
        if teacher is None:
            raise TeacherNotFoundError(code)

        teacher_tg = db_sess.query(Teacher).filter(Teacher.tg_user_id == tg_id).first()
        if not (teacher_tg is None) and teacher_tg.code != code:
            raise TeacherDuplicateTgUserIdError(tg_id)


        teacher.tg_user_id = tg_id
        db_sess.commit()

        return make_response('HTTP 200 OK', 200)
    except (TeacherDuplicateTgUserIdError, TeacherNotFoundError, RequestDataKeysError, RequestDataMissedKeyError,
            RequestDataTypeError) as error:
        logging.warning(error)
        return make_response('HTTP 400 Bad Request', 400)


@blueprint.route('/teacher', methods=['POST', 'GET'])
def teachers_post_get():
    try:
        db_sess = db_session.create_session()
        data_json = flask.request.json

        if flask.request.method == 'POST':
            request_data_validate.teachers_post_validate(data_json)
            teacher_list = []
            for teacher_json in data_json['teachers']:
                request_data_validate.teacher_post_validate(teacher_json)

                code = generate_unique_code(db_sess, Teacher)

                teacher_list.append(Teacher(
                    name=teacher_json['name'],
                    surname=teacher_json['surname'],
                    patronymic=teacher_json['patronymic'],
                    class_name=teacher_json['class_name'],
                    school_name=teacher_json['school_name'],
                    code=code
                ))

            db_sess.add_all(teacher_list)
            db_sess.commit()

            return make_response('HTTP 200 OK', 200)

        if flask.request.method == 'GET':
            request_data_validate.teachers_get_validate(data_json)
            school_name = data_json['school_name']

            teacher_list = db_sess.query(Teacher).filter(Teacher.school_name == school_name).all()
            if len(teacher_list) == 0:
                raise TeachersFromSchoolNotFoundError(school_name)

            teacher_dict_list = []
            for teacher in teacher_list:
                teacher_dict = {
                    'name': teacher.name,
                    'surname': teacher.surname,
                    'patronymic': teacher.patronymic,
                    'class_name': teacher.class_name,
                    'school_name': teacher.school_name,
                    'code': teacher.code
                }

                if not (teacher.tg_user_id is None):
                    teacher_dict['tg_user_id'] = teacher.tg_user_id

                teacher_dict_list.append(teacher_dict)

            return make_response({"teachers": teacher_dict_list}, 200)
    except (TeachersFromSchoolNotFoundError, SchoolNotFoundError, RequestDataKeysError, RequestDataMissedKeyError,
            RequestDataTypeError) as error:
        logging.warning(error)
        return make_response('HTTP 400 Bad Request', 400)


@blueprint.route('/student/absent', methods=['POST', 'GET'])
def student_absent():
    try:
        db_sess = db_session.create_session()
        data_json = flask.request.json
        student_id = 0

        if flask.request.method == 'POST':
            request_data_validate.student_absent_post_validate(data_json)

            date = datetime.datetime.strptime(data_json['date'], string_date_format).date()

            if 'code' in data_json.keys():
                student_code = data_json['code']
                student = db_sess.query(Student).filter(Student.code == student_code).first()

                if student is None:
                    raise StudentNotFoundError(student_code=student_code)

                student_id = student.id

            if 'tg_user_id' in data_json.keys():
                tg_user_id = data_json['tg_user_id']
                student = db_sess.query(Student).filter(Student.tg_user_id == tg_user_id).first()

                if student is None:
                    raise StudentNotFoundError(student_tg_user_id=tg_user_id)

                student_id = student.id

            absents = db_sess.query(Absent).filter(Absent.student_id == student_id).all()

            for absent in absents:
                if absent.date == date:
                    raise StudentDuplicateAbsent(date, student_id)


            absent = Absent(
                date=date,
                reason=data_json['reason'],
                student_id=student_id
            )

            if 'file' in flask.request.files.keys():
                file = flask.request.files['file']
                absent.file = file.read()

            db_sess.add(absent)
            db_sess.commit()

            return make_response('HTTP 200 OK', 200)

        if flask.request.method == 'GET':
            request_data_validate.student_absent_get_validate(data_json)

            if 'code' in data_json.keys():
                student_code = data_json['code']
                student = db_sess.query(Student).filter(Student.code == student_code).first()

                if student is None:
                    raise StudentNotFoundError(student_code=student_code)

                student_id = student.id

            if 'tg_user_id' in data_json.keys():
                student = db_sess.query(Student).filter(Student.tg_user_id == data_json['tg_user_id']).first()

                if student is None:
                    raise StudentNotFoundError(student_tg_user_id=data_json['tg_user_id'])

                student_id = student.id

            absents = db_sess.query(Absent).filter(Absent.student_id == student_id).all()

            absent_json_list = []
            for absent in absents:
                absent_json = {
                    "date": absent.date,
                    "reason": absent.reason,
                }

                if not (absent.file is None):
                    absent_json['file'] = absent.file

                absent_json_list.append(absent_json)

            return make_response({"absents": absent_json_list}, 200)
    except (StudentDuplicateAbsent, StudentNotFoundError, RequestDataKeysError, RequestDataMissedKeyError,
            RequestDataTypeError) as error:
        logging.warning(error)
        return make_response('HTTP 400 Bad Request', 400)


@blueprint.route('/student/tg_auth', methods=['POST'])
def student_tg_auth():
    try:
        data_json = flask.request.json
        request_data_validate.student_tg_auth_validate(data_json)

        code = data_json['code']
        tg_id = data_json['tg_user_id']

        db_sess = db_session.create_session()

        student = db_sess.query(Student).filter(Student.code == code).first()
        if student is None:
            raise StudentNotFoundError(code)

        student_tg = db_sess.query(Student).filter(Student.tg_user_id == tg_id).first()
        if not (student_tg is None) and student_tg.code != code:
            raise StudentDuplicateTgUserIdError(tg_id)

        student.tg_user_id = tg_id
        db_sess.commit()

        return make_response('HTTP 200 OK', 200)
    except (StudentDuplicateTgUserIdError, StudentNotFoundError, RequestDataKeysError, RequestDataMissedKeyError,
            RequestDataTypeError) as error:
        logging.warning(error)
        return make_response('HTTP 400 Bad Request', 400)


@blueprint.route('/student', methods=['POST', 'GET'])
def students_post_get():
    try:
        db_sess = db_session.create_session()
        data_json = flask.request.json

        if flask.request.method == 'POST':
            request_data_validate.students_post_validate(data_json)

            student_list = []
            for teacher_json in data_json['students']:
                request_data_validate.student_post_validate(teacher_json)

                code = generate_unique_code(db_sess, Teacher)

                student_list.append(Student(
                    name=teacher_json['name'],
                    surname=teacher_json['surname'],
                    patronymic=teacher_json['patronymic'],
                    class_name=teacher_json['class_name'],
                    school_name=teacher_json['school_name'],
                    code=code
                ))

            db_sess.add_all(student_list)
            db_sess.commit()
            return make_response('HTTP 200 OK', 200)

        if flask.request.method == 'GET':
            request_data_validate.students_get_validate(data_json)
            school_name = data_json['school_name']

            student_list = db_sess.query(Student).filter(Student.school_name == school_name).all()
            if len(student_list) == 0:
                raise SchoolNotFoundError(school_name)

            student_dict_list = []
            for student in student_list:
                student_dict = {
                        'name': student.name,
                        'surname': student.surname,
                        'patronymic': student.patronymic,
                        'class_name': student.class_name,
                        'school_name': student.school_name,
                        'code': student.code
                    }

                if not (student.tg_user_id is None):
                    student_dict['tg_user_id'] = student.tg_user_id

                student_dict_list.append(student_dict)

            return make_response({"students": student_dict_list}, 200)
    except (SchoolNotFoundError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return make_response('HTTP 400 Bad Request', 400)


@blueprint.route('/school', methods=['POST'])
def school_post():
    try:
        data_json = flask.request.json
        request_data_validate.school_post_validate(data_json)
        db_sess = db_session.create_session()
        school = School(name=data_json['school_name'])
        db_sess.add(school)
        db_sess.commit()

        return make_response('HTTP 200 OK', 200)
    except (RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return make_response('HTTP 400 Bad Request', 400)


@blueprint.route('/absent', methods=['GET'])
def absents_get():
    try:
        db_sess = db_session.create_session()
        data_json = flask.request.json

        request_data_validate.absents_get_validate(data_json)

        school_name = data_json['school_name']
        absents = []

        students = db_sess.query(Student).filter(Student.school_name == school_name).all()
        for student in students:
            absents += student.absents

        absent_json_list = []
        for absent in absents:
            absent_json = {
                "date": absent.date,
                "reason": absent.reason,
            }

            if not (absent.file is None):
                absent_json['file'] = absent.file

            absent_json_list.append(absent_json)

        return make_response({"absents": absent_json_list}, 200)
    except (RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return make_response('HTTP 400 Bad Request', 400)


# @blueprint.route('/teacher', methods=['POST', 'PATCH'])
# def teacher_post():
#     try:
#         request_json = flask.request.json
#
#         db_sess = db_session.create_session()
#         if flask.request.method == 'POST':
#             request_data_validate.teacher_post_validate(request_json)
#             teacher = Teacher(
#                 tg_user_id=request_json["tg_user_id"],
#                 name=request_json["name"],
#                 surname=request_json["surname"],
#                 patronymic=request_json["patronymic"],
#                 class_name=request_json["class_name"],
#                 code=random.randint()
#             )
#
#             teacher.set_password(request_json['password'])
#             db_sess.add(teacher)
#
#         if flask.request.method == 'PATCH':
#             teacher = db_sess.query(Teacher).get(request_json['id'])
#             if teacher is None:
#                 raise TeacherNotFoundError(request_json["id"])
#             request_data_validate.teacher_patch_validate(request_json)
#
#             for key, value in request_json.items():
#                 teacher[key] = value
#
#         db_sess.commit()
#         return make_response('HTTP 200 OK', 200)
#     except (TeacherNotFoundError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
#         logging.warning(error)
#         return make_response('HTTP 400 Bad Request', 400)
#
#
# @blueprint.route('/teacher/<int:teacher_id>', methods=['GET'])
# def teacher_get(teacher_id):
#     try:
#         db_sess = db_session.create_session()
#         teacher = db_sess.query(Teacher).get(teacher_id)
#
#         if teacher is None:
#             raise TeacherNotFoundError(teacher_id)
#
#         return make_response(json.dumps({
#                 'name': teacher.name,
#                 'surname': teacher.surname,
#                 'patronymic': teacher.patronymic,
#                 'class_name': teacher.class_name
#             }), 200)
#
#     except TeacherNotFoundError as error:
#         logging.warning(error)
#         return make_response('HTTP 400 Bad Request', 400)
