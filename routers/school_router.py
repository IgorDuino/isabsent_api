import logging
import routers.models as json_body

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from data.student import Student
from tools.error_book import *
from data import db_session
from data.school import School
from data.teacher import Teacher
from tools.settings import string_date_format
from tools.tools import generate_unique_code
from google_spreadsheets.google_spread_sheets import google_spread_sheets


school_router = APIRouter()


@school_router.post('/school',
                    summary='Add new school',
                    status_code=status.HTTP_201_CREATED,
                    responses={201: {"model": json_body.OkResponse, "description": "School has been added"},
                               400: {"model": json_body.BadResponse}})
def school_post(body: json_body.School):
    """
        Add new school, all parameters are required:

        - **school_name**: school name
        - **link**: link to google spreadsheets
    """
    try:
        db_sess = db_session.create_session()

        school = db_sess.query(School).get(body.school_name)
        if school is not None:
            raise SchoolDuplicateError(body.school_name)

        school = School(
            name=body.school_name,
            link=body.link
        )
        db_sess.add(school)
        db_sess.commit()

        return JSONResponse(content=json_body.OkResponse(msg='HTTP_201_CREATED').dict(),
                            status_code=status.HTTP_201_CREATED)
    except (SchoolDuplicateError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return JSONResponse(content=json_body.BadResponse(error_msg=str(error)).dict(),
                            status_code=status.HTTP_400_BAD_REQUEST)


@school_router.get('/schools',
                   summary='Get school list',
                   status_code=status.HTTP_200_OK,
                   responses={200: {"model": json_body.SchoolList, "description": "Successful response"},
                              400: {"model": json_body.BadResponse}})
def schools_get():
    """
        Get school list, no parameters need
    """
    try:
        db_sess = db_session.create_session()

        school_list = db_sess.query(School).all()

        response_dict = json_body.SchoolList(schools=[])
        for school in school_list:
            response_dict.schools.append(json_body.School(school_name=school.name, link=school.link))

        return JSONResponse(content=response_dict.dict(),
                            status_code=status.HTTP_200_OK)
    except (SchoolDuplicateError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return JSONResponse(content=json_body.BadResponse(error_msg=str(error)).dict(),
                            status_code=status.HTTP_400_BAD_REQUEST)


@school_router.post('/school/teachers',
                    summary='Add list of teachers',
                    status_code=status.HTTP_201_CREATED,
                    responses={201: {"model": json_body.OkResponse, "description": "Teachers has been added"},
                               400: {"model": json_body.BadResponse}})
def teachers_post(body: json_body.TeacherListPost):
    """
        Add teacher list to given school:

        - **school_name**: school name, required
        - **teachers**: list of teachers, not required, if not given, teachers will take from google spreadsheets
    """
    try:
        db_sess = db_session.create_session()
        from_sheet_flag = False

        school_name = body.school_name
        school = db_sess.query(School).get(school_name)
        if school is None:
            raise SchoolNotFoundError(school_name)

        if body.teachers is None:
            body.teachers = google_spread_sheets.google_sheets_get_teachers(school.link, school_name)
            from_sheet_flag = True

        teacher_list = []
        teacher_code_list = []
        for teacher_json in body.teachers:
            code = generate_unique_code(db_sess)

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

        return JSONResponse(content=json_body.OkResponse(msg='HTTP_201_CREATED').dict(),
                            status_code=status.HTTP_201_CREATED)
    except (StudentNotFoundError, SchoolNotFoundError, RequestDataKeysError,
            RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return JSONResponse(content=json_body.BadResponse(error_msg=str(error)).dict(),
                            status_code=status.HTTP_400_BAD_REQUEST)


@school_router.get('/school/teachers',
                   summary='Get list of teachers',
                   status_code=status.HTTP_200_OK,
                   responses={200: {"model": json_body.TeacherListGet, "description": "Success response"},
                              400: {"model": json_body.BadResponse}})
def teachers_get(school_name: str):
    """
        Get teacher list from given school:

        - **school_name**: school name, required
    """
    try:
        db_sess = db_session.create_session()

        school = db_sess.query(School).get(school_name)
        if school is None:
            raise SchoolNotFoundError(school_name)

        teacher_list = db_sess.query(Teacher).filter(Teacher.school_name == school_name).all()

        teacher_dict_list = json_body.TeacherListGet(teachers=[])
        for teacher in teacher_list:
            response = json_body.TeacherGet(
                name=teacher.name,
                surname=teacher.surname,
                patronymic=teacher.patronymic,
                class_name=teacher.class_name,
                school_name=teacher.school_name,
                code=teacher.code
            )

            if not (teacher.tg_user_id is None):
                response.tg_user_id = teacher.tg_user_id

            teacher_dict_list.teachers.append(response)

        return JSONResponse(content=teacher_dict_list.dict(), status_code=status.HTTP_200_OK)
    except (StudentNotFoundError, SchoolNotFoundError, RequestDataKeysError,
            RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return JSONResponse(content=json_body.BadResponse(error_msg=str(error)).dict(),
                            status_code=status.HTTP_400_BAD_REQUEST)


@school_router.get('/school/absents',
                   summary='Get list of absents',
                   status_code=status.HTTP_200_OK,
                   responses={200: {"model": json_body.AbsentList, "description": "Successful response"},
                              400: {"model": json_body.BadResponse}})
def absents_get(school_name: str):
    """
       Get absent list from given school:

       - **school_name**: school name, required
   """
    try:
        db_sess = db_session.create_session()
        absents = []

        students = db_sess.query(Student).filter(Student.school_name == school_name).all()
        for student in students:
            absents += student.absents

        absent_json_list = json_body.AbsentList(absents=[])
        for absent in absents:
            student = absent.student
            absent_json = {
                "date": datetime.date.strftime(absent.date, string_date_format),
                "reason": absent.reason,
                "code": student.code
            }

            if not (absent.file is None):
                absent_json['file'] = absent.file

            absent_json_list.absents.append(absent_json)

        return JSONResponse(content=absent_json_list.dict(), status_code=status.HTTP_200_OK)
    except (RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return JSONResponse(content=json_body.BadResponse(error_msg=str(error)).dict(),
                            status_code=status.HTTP_400_BAD_REQUEST)


@school_router.post('/school/students',
                    summary='Add list of students',
                    status_code=status.HTTP_201_CREATED,
                    responses={201: {"model": json_body.OkResponse, "description": "Students has been added"},
                               400: {"model": json_body.BadResponse}})
def students_post(body: json_body.StudentListPost):
    """
        Add student list to given school:

        - **school_name**: school name, required
        - **teachers**: list of students, not required, if not given, teachers will take from google spreadsheets
    """
    try:
        db_sess = db_session.create_session()
        from_sheet_flag = False

        school_name = body.school_name
        school = db_sess.query(School).get(school_name)
        if school is None:
            raise SchoolNotFoundError(school_name)

        if body.students is None:
            body.students = google_spread_sheets.google_sheets_get_students(school.link, school_name)
            from_sheet_flag = True

        student_list = []
        student_code_list = []

        for student_json in body.students:
            code = generate_unique_code(db_sess)

            student_list.append(Student(
                name=student_json['name'],
                surname=student_json['surname'],
                patronymic=student_json['patronymic'],
                class_name=student_json['class_name'],
                school_name=school_name,
                code=code
            ))

            student_code_list.append([code])

        db_sess.add_all(student_list)
        db_sess.commit()

        if from_sheet_flag:
            link = school.link
            google_spread_sheets.google_sheets_students_codes(link, student_code_list)

        return JSONResponse(content=json_body.OkResponse(msg='HTTP_201_CREATED').dict(),
                            status_code=status.HTTP_201_CREATED)
    except (SchoolNotFoundError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return JSONResponse(content=json_body.BadResponse(error_msg=str(error)).dict(),
                            status_code=status.HTTP_400_BAD_REQUEST)


@school_router.get('/school/students',
                   summary='Get list of students',
                   status_code=status.HTTP_200_OK,
                   responses={200: {"model": json_body.StudentListGet, "description": "Success response"},
                              400: {"model": json_body.BadResponse}})
def students_get(school_name: str):
    """
        Get student list from given school:

        - **school_name**: school name, required
    """
    try:
        db_sess = db_session.create_session()

        student_list = db_sess.query(Student).filter(Student.school_name == school_name).all()

        student_dict_list = json_body.StudentListGet(students=[])
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

            student_dict_list.students.append(student_dict)

        return JSONResponse(content=student_dict_list.dict(), status_code=status.HTTP_200_OK)
    except (SchoolNotFoundError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return JSONResponse(content=json_body.BadResponse(error_msg=str(error)),
                            status_code=status.HTTP_400_BAD_REQUEST.dict())


@school_router.get('/school/find_by_code',
                   summary='Get information about teacher',
                   status_code=status.HTTP_200_OK,
                   response_model=json_body.Teacher,
                   responses={200: {"model": json_body.StudentTeacher, "description": "Successful Response"},
                              400: {"model": json_body.BadResponse}})
def find_by_code(code: str = None, tg_user_id: int = None):
    """
        Get information about teacher with given code or tg user id, only one of parameters is required:

        - **code**: unique code, all teachers have this code
        - **tg_user_id**: unique telegram user id
    """
    try:
        db_sess = db_session.create_session()

        if not (code is None):
            teacher = db_sess.query(Teacher).filter(Teacher.code == code).first()
            student = db_sess.query(Student).filter(Student.code == code).first()

            if not (teacher is None):
                response_body = json_body.StudentTeacher(
                    name=teacher.name,
                    surname=teacher.surname,
                    patronymic=teacher.patronymic,
                    class_name=teacher.class_name,
                    school_name=teacher.school_name,
                    type='teacher'
                )

                if not (teacher.tg_user_id is None):
                    response_body.tg_user_id = teacher.tg_user_id

            elif not (student is None):
                response_body = json_body.StudentTeacher(
                    name=student.name,
                    surname=student.surname,
                    patronymic=student.patronymic,
                    class_name=student.class_name,
                    school_name=student.school_name,
                    type='student'
                )

                if not (student.tg_user_id is None):
                    response_body.tg_user_id = student.tg_user_id

            else:
                raise StudentTeacherNotFoundError(code=code)

            return JSONResponse(content=response_body.dict(), status_code=status.HTTP_200_OK)

        elif not (tg_user_id is None):
            teacher = db_sess.query(Teacher).filter(Teacher.tg_user_id == tg_user_id).first()
            student = db_sess.query(Student).filter(Student.tg_user_id == tg_user_id).first()

            if not (teacher is None):
                response_body = json_body.StudentTeacher(
                    name=teacher.name,
                    surname=teacher.surname,
                    patronymic=teacher.patronymic,
                    class_name=teacher.class_name,
                    school_name=teacher.school_name,
                    tg_user_id=teacher.tg_user_id,
                    type='teacher'
                )

            elif not (student is None):
                response_body = json_body.StudentTeacher(
                    name=student.name,
                    surname=student.surname,
                    patronymic=student.patronymic,
                    class_name=student.class_name,
                    school_name=student.school_name,
                    tg_user_id=student.tg_user_id,
                    type='student'
                )
            else:
                raise StudentTeacherNotFoundError(tg_user_id=tg_user_id)

            return JSONResponse(content=response_body.dict(), status_code=status.HTTP_200_OK)
        else:
            raise RequestDataKeysError([], ['code', 'tg_user_id'])

    except (TeacherNotFoundError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError,
            StudentTeacherNotFoundError) as error:
        logging.warning(error)
        return JSONResponse(content=json_body.BadResponse(error_msg=str(error)).dict(),
                            status_code=status.HTTP_400_BAD_REQUEST)
