import base64
import logging
import routers.models as json_body

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from tools.error_book import *
from data import db_session
from tools.settings import *
from data.student import Student
from data.absent import Absent
from tools.tools import generate_unique_code
from google_spreadsheets.google_spread_sheets import google_spread_sheets


student_router = APIRouter()


@student_router.post('/student/absent',
                     summary='Add student absent',
                     status_code=status.HTTP_201_CREATED,
                     responses={201: {"model": json_body.OkResponse, "description": "Absent has been added"},
                                400: {"model": json_body.BadResponse}})
def student_absent_post(body: json_body.StudentAbsent):
    """
        Add student absent in db and google spreadsheets:

        - **code**: unique code, all teachers have this code, not required
        - **tg_user_id**: unique telegram user id, not required
        - **date**: date when student will absent, required
        - **reason** absent`s reason, required
        - **file** photo or file of official proof, not required
    """
    try:
        db_sess = db_session.create_session()
        student_id = 0
        student = None
        link = ''

        date = datetime.datetime.strptime(body.date, string_date_format).date()

        if not (body.code is None):
            student_code = body.code
            student = db_sess.query(Student).filter(Student.code == student_code).first()

            if student is None:
                raise StudentNotFoundError(student_code=student_code)

            student_id = student.id
            school = student.school
            link = school.link

        elif not(body.tg_user_id is None):
            tg_user_id = body.tg_user_id
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
            reason=body.reason,
            student_id=student_id
        )

        name = student.name
        surname = student.surname
        patronymic = student.patronymic
        class_name = student.class_name

        if not (body.file is None):
            file = body.file
            absent.file = base64.b64encode(file)
            google_spread_sheets.google_sheets_student_absent(link, date, body.reason, name, surname,
                                                              patronymic, class_name)
        else:
            google_spread_sheets.google_sheets_student_absent(link, date, body.reason, name, surname,
                                                              patronymic, class_name)

        db_sess.add(absent)
        db_sess.commit()

        return JSONResponse(content=json_body.OkResponse(msg='HTTP_201_CREATED').dict(),
                            status_code=status.HTTP_201_CREATED)

    except (StudentDuplicateAbsent, StudentNotFoundError, RequestDataKeysError, RequestDataMissedKeyError,
            RequestDataTypeError) as error:
        logging.warning(error)
        return JSONResponse(content=json_body.BadResponse(error_msg=str(error)).dict(),
                            status_code=status.HTTP_400_BAD_REQUEST)


@student_router.get('/student/absent',
                    summary='Get student absent list',
                    status_code=status.HTTP_200_OK,
                    responses={200: {"model": json_body.StudentAbsentList, "description": "Successful Response"},
                               400: {"model": json_body.BadResponse}})
def student_absent_get(body: json_body.StudentCodeTgUserId):
    """
        Get student absents by code or tg user id, only one of parameters is required:

        - **code**: unique code, all teachers have this code
        - **tg_user_id**: unique telegram user id
    """
    try:
        db_sess = db_session.create_session()
        student_id = 0

        if not (body.code is None):
            student_code = body.code
            student = db_sess.query(Student).filter(Student.code == student_code).first()

            if student is None:
                raise StudentNotFoundError(student_code=student_code)

            student_id = student.id

        elif not (body.tg_user_id is None):
            student = db_sess.query(Student).filter(Student.tg_user_id == body.tg_user_id).first()

            if student is None:
                raise StudentNotFoundError(student_tg_user_id=body.tg_user_id)

            student_id = student.id

        absents = db_sess.query(Absent).filter(Absent.student_id == student_id).all()

        absent_list = json_body.StudentAbsentList(absents=[])
        for absent in absents:
            absent_json = {
                "date": datetime.date.strftime(absent.date, string_date_format),
                "reason": absent.reason,
            }

            if not (absent.file is None):
                absent_json['file'] = str(absent.file)

            absent_list.absents.append(absent_json)
        print(absent_list)

        return JSONResponse(content=absent_list.dict(), status_code=status.HTTP_200_OK)

    except (StudentDuplicateAbsent, StudentNotFoundError, RequestDataKeysError, RequestDataMissedKeyError,
            RequestDataTypeError) as error:
        logging.warning(error)
        return JSONResponse(content=json_body.BadResponse(error_msg=str(error)).dict(),
                            status_code=status.HTTP_400_BAD_REQUEST)


@student_router.post('/student/tg_auth',
                     summary='',
                     status_code=status.HTTP_200_OK,
                     responses={201: {"model": json_body.OkResponse, "description": "Tg user id has been bind"},
                                400: {"model": json_body.BadResponse}})
def student_tg_auth(body: json_body.StudentTgAuth):
    """
        Binding tg user id to teacher code, all parameters are required:

        - **code**: unique code, all teachers have this code
        - **tg_user_id**: unique telegram user id
    """
    try:
        code = body.code
        tg_id = body.tg_user_id

        db_sess = db_session.create_session()

        student = db_sess.query(Student).filter(Student.code == code).first()
        if student is None:
            raise StudentNotFoundError(code)

        student_tg = db_sess.query(Student).filter(Student.tg_user_id == tg_id).first()
        if not (student_tg is None) and student_tg.code != code:
            raise StudentDuplicateTgUserIdError(tg_id)

        student.tg_user_id = tg_id
        db_sess.commit()

        return JSONResponse(content=json_body.OkResponse(msg='HTTP_201_CREATED').dict(),
                            status_code=status.HTTP_201_CREATED)
    except (StudentDuplicateTgUserIdError, StudentNotFoundError, RequestDataKeysError, RequestDataMissedKeyError,
            RequestDataTypeError) as error:
        logging.warning(error)
        return JSONResponse(content=json_body.BadResponse(error_msg=str(error)).dict(),
                            status_code=status.HTTP_400_BAD_REQUEST)


@student_router.post('/student/code',
                     summary='Generating new code for student',
                     status_code=status.HTTP_201_CREATED,
                     responses={201: {"model": json_body.OkResponse, "description": "New code generate success"},
                                400: {"model": json_body.BadResponse}})
def student_pass(body: json_body.StudentCodeTgUserId):
    """
        Generating new code for student, only one of parameters is required:

        - **code**: unique code, all teachers have this code
        - **tg_user_id**: unique telegram user id
    """
    try:
        link = ''
        old_code = ''

        db_sess = db_session.create_session()
        gen_code = generate_unique_code(db_sess)
        if not (body.code is None):
            code = body.code

            student = db_sess.query(Student).filter(Student.code == code).first()
            if student is None:
                raise StudentNotFoundError(student_code=code)

            student.code = gen_code
            school = student.school
            link = school.link
            old_code = code

        elif not (body.tg_user_id is None):
            tg_id = body.tg_user_id

            student = db_sess.query(Student).filter(Student.tg_user_id == tg_id).first()
            if student is None:
                raise StudentNotFoundError(student_tg_user_id=tg_id)

            old_code = student.code
            student.code = gen_code
            school = student.school
            link = school.link

        db_sess.commit()

        google_spread_sheets.google_sheets_student_code_generate(link, old_code, gen_code)

        return JSONResponse(content=json_body.OkResponse(msg='HTTP_201_CREATED').dict(),
                            status_code=status.HTTP_201_CREATED)
    except (StudentNotFoundError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return JSONResponse(content=json_body.BadResponse(error_msg=str(error)).dict(),
                            status_code=status.HTTP_400_BAD_REQUEST)


@student_router.get('/student',
                    summary='Get information about student',
                    status_code=status.HTTP_200_OK,
                    response_model=json_body.Teacher,
                    responses={200: {"model": json_body.Student, "description": "Successful Response"},
                               400: {"model": json_body.BadResponse}})
def student_get(body: json_body.StudentCodeTgUserId):
    """
        Get information about student with given code or tg user id, only one of parameters is required:

        - **code**: unique code, all teachers have this code
        - **tg_user_id**: unique telegram user id
    """
    try:
        db_sess = db_session.create_session()
        if not (body.code is None):
            code = body.code
            student = db_sess.query(Student).filter(Student.code == code).first()

            if student is None:
                raise StudentNotFoundError(student_code=code)

            response_body = json_body.Student(
                name=student.name,
                surname=student.surname,
                patronymic=student.patronymic,
                class_name=student.class_name,
                school_name=student.school_name
            )

            if not (student.tg_user_id is None):
                response_body.tg_user_id = student.tg_user_id

            return JSONResponse(content=response_body.dict(), status_code=status.HTTP_200_OK)

        elif not (body.tg_user_id is None):
            tg_user_id = body.tg_user_id

            student = db_sess.query(Student).filter(Student.tg_user_id == tg_user_id).first()

            if student is None:
                raise StudentNotFoundError(student_tg_user_id=tg_user_id)

            response_body = json_body.Student(
                name=student.name,
                surname=student.surname,
                patronymic=student.patronymic,
                class_name=student.class_name,
                school_name=student.school_name,
                tg_user_id=student.tg_user_id
            )

            return JSONResponse(content=response_body.dict(), status_code=status.HTTP_200_OK)

    except (StudentNotFoundError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return JSONResponse(content=json_body.BadResponse(error_msg=str(error)).dict(),
                            status_code=status.HTTP_400_BAD_REQUEST)
