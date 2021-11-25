import flask
import logging

from flask import make_response
from tools.error_book import *
from data import db_session
from tools import request_data_validate
from tools.settings import *
from data.student import Student
from data.teacher import Teacher
from data.school import School
from data.absent import Absent
from tools.tools import generate_unique_code
from google_spreadsheets.google_spread_sheets import GoogleSpreadSheetsApi


blueprint = flask.Blueprint(
    'sdo_parser_api',
    __name__,
)


google_spread_sheets = GoogleSpreadSheetsApi('google_spreadsheets/google_credentials.json')


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


@blueprint.route('/teacher/code', methods=['POST'])
def teacher_pass():
    """Generating new code for teacher"""
    try:
        link = ''
        old_code = ''
        data_json = flask.request.json
        request_data_validate.teacher_gen_password_validate(data_json)

        db_sess = db_session.create_session()
        gen_code = generate_unique_code(db_sess, Teacher)
        if 'code' in data_json.keys():
            code = data_json['code']

            teacher = db_sess.query(Teacher).filter(Teacher.code == code).first()
            if teacher is None:
                raise TeacherNotFoundError(teacher_code=code)

            teacher.code = gen_code
            school = teacher.school
            link = school.link
            old_code = code

        elif 'tg_user_id' in data_json.keys():
            tg_id = data_json['tg_user_id']

            teacher = db_sess.query(Teacher).filter(Teacher.tg_user_id == tg_id).first()
            if teacher is None:
                raise TeacherNotFoundError(teacher_tg_user_id=tg_id)

            old_code = teacher.code
            teacher.code = gen_code
            school = teacher.school
            link = school.link

        db_sess.commit()

        google_spread_sheets.google_sheets_teacher_code_generate(link, old_code, gen_code)

        return make_response('HTTP 200 OK', 200)
    except (TeacherNotFoundError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return make_response('HTTP 400 Bad Request', 400)


@blueprint.route('/teacher', methods=['GET'])
def teacher_get():
    try:
        db_sess = db_session.create_session()
        data_json = flask.request.json

        request_data_validate.teacher_get_validate(data_json)
        if 'code' in data_json.keys():
            code = data_json['code']
            teacher = db_sess.query(Teacher).filter(Teacher.code == code).first()

            if teacher is None:
                raise TeacherNotFoundError(teacher_code=code)

            response_dict = {
                'name': teacher.name,
                'surname': teacher.surname,
                'patronymic': teacher.patronymic,
                'class_name': teacher.class_name,
                'school_name': teacher.school_name
            }

            if not (teacher.tg_user_id is None):
                response_dict['tg_user_id'] = teacher.tg_user_id

            return make_response(response_dict, 200)

        if 'tg_user_id' in data_json.keys():
            tg_user_id = data_json['tg_user_id']

            teacher = db_sess.query(Teacher).filter(Teacher.tg_user_id == tg_user_id).first()

            if teacher is None:
                raise TeacherNotFoundError(teacher_tg_user_id=tg_user_id)

            return make_response({
                'name': teacher.name,
                'surname': teacher.surname,
                'patronymic': teacher.patronymic,
                'class_name': teacher.class_name,
                'school_name': teacher.school_name,
                'tg_user_id': tg_user_id
            }, 200)

    except (TeacherNotFoundError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return make_response('HTTP 400 Bad Request', 400)


@blueprint.route('/student/absent', methods=['POST', 'GET'])
def student_absent():
    try:
        db_sess = db_session.create_session()
        data_json = flask.request.json
        student_id = 0
        student = None
        link = ''

        if flask.request.method == 'POST':
            request_data_validate.student_absent_post_validate(data_json)

            date = datetime.datetime.strptime(data_json['date'], string_date_format).date()

            if 'code' in data_json.keys():
                student_code = data_json['code']
                student = db_sess.query(Student).filter(Student.code == student_code).first()

                if student is None:
                    raise StudentNotFoundError(student_code=student_code)

                student_id = student.id
                school = student.school
                link = school.link

            if 'tg_user_id' in data_json.keys():
                tg_user_id = data_json['tg_user_id']
                student = db_sess.query(Student).filter(Student.tg_user_id == tg_user_id).first()

                if student is None:
                    raise StudentNotFoundError(student_tg_user_id=tg_user_id)

                student_id = student.id
                school = student.school
                link = school.link

            absents = db_sess.query(Absent).filter(Absent.student_id == student_id).all()

            for absent in absents:
                if absent.date == date:
                    raise StudentDuplicateAbsent(date, student_id)

            absent = Absent(
                date=date,
                reason=data_json['reason'],
                student_id=student_id
            )

            name = student.name
            surname = student.surname
            patronymic = student.patronymic
            class_name = student.class_name

            if 'file' in data_json:
                file = data_json['file']
                absent.file = file.read()
                google_spread_sheets.google_sheets_student_absent(link, date, data_json['reason'], name, surname,
                                                                  patronymic, class_name, file.read())
            else:
                google_spread_sheets.google_sheets_student_absent(link, date, data_json['reason'], name, surname,
                                                                  patronymic, class_name)

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


@blueprint.route('/student/code', methods=['POST'])
def student_pass():
    """Generating new code for student"""
    try:
        link = ''
        old_code = ''
        data_json = flask.request.json
        request_data_validate.student_gen_password_validate(data_json)

        db_sess = db_session.create_session()
        gen_code = generate_unique_code(db_sess, Student)
        if 'code' in data_json.keys():
            code = data_json['code']

            student = db_sess.query(Student).filter(Student.code == code).first()
            if student is None:
                raise StudentNotFoundError(student_code=code)

            student.code = gen_code
            school = student.school
            link = school.link
            old_code = code

        elif 'tg_user_id' in data_json.keys():
            tg_id = data_json['tg_user_id']

            student = db_sess.query(Student).filter(Student.tg_user_id == tg_id).first()
            if student is None:
                raise StudentNotFoundError(student_tg_user_id=tg_id)

            old_code = student.code
            student.code = gen_code
            school = student.school
            link = school.link

        db_sess.commit()

        google_spread_sheets.google_sheets_student_code_generate(link, old_code, gen_code)

        return make_response('HTTP 200 OK', 200)
    except (StudentNotFoundError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return make_response('HTTP 400 Bad Request', 400)


@blueprint.route('/student', methods=['GET'])
def student_get():
    try:
        db_sess = db_session.create_session()
        data_json = flask.request.json

        request_data_validate.student_get_validate(data_json)
        if 'code' in data_json.keys():
            code = data_json['code']
            student = db_sess.query(Student).filter(Student.code == code).first()

            if student is None:
                raise StudentNotFoundError(student_code=code)

            return make_response({
                'name': student.name,
                'surname': student.surname,
                'patronymic': student.patronymic,
                'class_name': student.class_name,
                'school_name': student.school_name
            }, 200)

        if 'tg_user_id' in data_json.keys():
            tg_user_id = data_json['tg_user_id']

            student = db_sess.query(Student).filter(Student.tg_user_id == tg_user_id).first()

            if student is None:
                raise StudentNotFoundError(student_tg_user_id=tg_user_id)

            return make_response({
                'name': student.name,
                'surname': student.surname,
                'patronymic': student.patronymic,
                'class_name': student.class_name,
                'school_name': student.school_name
            }, 200)

    except (StudentNotFoundError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return make_response('HTTP 400 Bad Request', 400)


@blueprint.route('/school', methods=['POST'])
def school_post():
    try:
        data_json = flask.request.json
        request_data_validate.school_post_validate(data_json)
        db_sess = db_session.create_session()

        school = db_sess.query(School).get(data_json['school_name'])
        if school is not None:
            raise SchoolDuplicateError(data_json['school_name'])

        school = School(
            name=data_json['school_name'],
            link=data_json['link']
        )
        db_sess.add(school)
        db_sess.commit()

        return make_response('HTTP 200 OK', 200)
    except (SchoolDuplicateError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return make_response('HTTP 400 Bad Request', 400)


@blueprint.route('school/teachers', methods=['POST', 'GET'])
def teachers_post_get():
    try:
        db_sess = db_session.create_session()
        data_json = flask.request.json
        from_sheet_flag = False

        if flask.request.method == 'POST':
            request_data_validate.teachers_post_validate(data_json)

            school_name = data_json['school_name']
            school = db_sess.query(School).get(school_name)
            if school is None:
                raise StudentNotFoundError(school_name)

            if len(data_json['teachers']) == 0:
                data_json = google_spread_sheets.google_sheets_get_teachers(school.link, school_name)
                from_sheet_flag = True

            teacher_list = []
            teacher_code_list = []
            for teacher_json in data_json['teachers']:
                request_data_validate.teacher_post_validate(teacher_json)

                code = generate_unique_code(db_sess, Teacher)

                teacher_list.append(Teacher(
                    name=teacher_json['name'],
                    surname=teacher_json['surname'],
                    patronymic=teacher_json['patronymic'],
                    class_name=teacher_json['class_name'],
                    school_name=school_name,
                    code=code
                ))

                teacher_code_list.append([code])

            db_sess.add_all(teacher_list)
            db_sess.commit()

            if from_sheet_flag:
                link = school.link
                google_spread_sheets.google_sheets_teachers_codes(link, teacher_code_list)

            return make_response('HTTP 200 OK', 200)

        if flask.request.method == 'GET':
            request_data_validate.teachers_get_validate(data_json)
            school_name = data_json['school_name']

            teacher_list = db_sess.query(Teacher).filter(Teacher.school_name == school_name).all()

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
    except (StudentNotFoundError, SchoolNotFoundError, RequestDataKeysError,
            RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return make_response('HTTP 400 Bad Request', 400)


@blueprint.route('school/students', methods=['POST', 'GET'])
def students_post_get():
    try:
        db_sess = db_session.create_session()
        data_json = flask.request.json
        from_sheet_flag = False

        if flask.request.method == 'POST':
            request_data_validate.students_post_validate(data_json)

            school_name = data_json['school_name']
            school = db_sess.query(School).get(school_name)
            if school is None:
                raise SchoolNotFoundError(school_name)

            if len(data_json['students']) == 0:
                data_json = google_spread_sheets.google_sheets_get_students(school.link, school_name)
                from_sheet_flag = True

            student_list = []
            student_code_list = []
            for teacher_json in data_json['students']:
                request_data_validate.student_post_validate(teacher_json)

                code = generate_unique_code(db_sess, Teacher)

                student_list.append(Student(
                    name=teacher_json['name'],
                    surname=teacher_json['surname'],
                    patronymic=teacher_json['patronymic'],
                    class_name=teacher_json['class_name'],
                    school_name=school_name,
                    code=code
                ))

                student_code_list.append([code])

            db_sess.add_all(student_list)
            db_sess.commit()

            if from_sheet_flag:
                link = school.link
                google_spread_sheets.google_sheets_students_codes(link, student_code_list)

            return make_response('HTTP 200 OK', 200)

        if flask.request.method == 'GET':
            request_data_validate.students_get_validate(data_json)
            school_name = data_json['school_name']

            student_list = db_sess.query(Student).filter(Student.school_name == school_name).all()

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


@blueprint.route('school/absents', methods=['GET'])
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
            student = absent.student
            absent_json = {
                "date": absent.date,
                "reason": absent.reason,
                "code": student.code
            }

            if not (absent.file is None):
                absent_json['file'] = absent.file

            absent_json_list.append(absent_json)

        return make_response({"absents": absent_json_list}, 200)
    except (RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return make_response('HTTP 400 Bad Request', 400)
