import logging

from fastapi import APIRouter, Response, status
from tools.error_book import *
from data import db_session
from data.teacher import Teacher
from tools.tools import generate_unique_code
from google_spreadsheets.google_spread_sheets import google_spread_sheets
import tools.models as json_body


teacher_router = APIRouter()


@teacher_router.post("/teacher/tg_auth",
                     summary='Binding tg user id to teacher code',
                     status_code=status.HTTP_201_CREATED)
def teacher_tg_auth(body: json_body.TeacherTgAuth):
    """
        Binding tg user id to teacher code, all parameters are required:

        - **code**: unique code, all teachers have this code
        - **tg_user_id**: unique telegram user id
    """

    try:
        code = body.code
        tg_id = body.tg_user_id

        db_sess = db_session.create_session()

        teacher = db_sess.query(Teacher).filter(Teacher.code == code).first()
        if teacher is None:
            raise TeacherNotFoundError(code)

        teacher_tg = db_sess.query(Teacher).filter(Teacher.tg_user_id == tg_id).first()
        if not (teacher_tg is None) and teacher_tg.code != code:
            raise TeacherDuplicateTgUserIdError(tg_id)

        teacher.tg_user_id = tg_id
        db_sess.commit()
        return Response(content='HTTP_201_CREATED', status_code=status.HTTP_201_CREATED)
    except (TeacherDuplicateTgUserIdError, TeacherNotFoundError, RequestDataKeysError, RequestDataMissedKeyError,
            RequestDataTypeError) as error:
        logging.warning(error)
        return Response(content=str(error), status_code=status.HTTP_400_BAD_REQUEST)


@teacher_router.post('/teacher/code',
                     summary='Generating new code for teacher',
                     status_code=status.HTTP_201_CREATED)
def teacher_pass(body: json_body.TeacherCodeTgUserId):
    """
        Generating new code for teacher, only one of parameters is required:

        - **code**: unique code, all teachers have this code
        - **tg_user_id**: unique telegram user id
    """
    try:
        link = ''
        old_code = ''

        db_sess = db_session.create_session()
        gen_code = generate_unique_code(db_sess, Teacher)
        if not (body.code is None):
            code = body.code

            teacher = db_sess.query(Teacher).filter(Teacher.code == code).first()
            if teacher is None:
                raise TeacherNotFoundError(teacher_code=code)

            teacher.code = gen_code
            school = teacher.school
            link = school.link
            old_code = code

        elif not (body.tg_user_id is None):
            tg_id = body.tg_user_id

            teacher = db_sess.query(Teacher).filter(Teacher.tg_user_id == tg_id).first()
            if teacher is None:
                raise TeacherNotFoundError(teacher_tg_user_id=tg_id)

            old_code = teacher.code
            teacher.code = gen_code
            school = teacher.school
            link = school.link

        db_sess.commit()

        google_spread_sheets.google_sheets_teacher_code_generate(link, old_code, gen_code)

        return Response(content='HTTP 200 OK', status_code=status.HTTP_200_OK)
    except (TeacherNotFoundError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return Response(content=str(error), status_code=status.HTTP_400_BAD_REQUEST)


@teacher_router.get('/teacher',
                    summary='Get information about teacher',
                    status_code=status.HTTP_200_OK,
                    response_model=json_body.Teacher)
def teacher_get(body: json_body.TeacherCodeTgUserId):
    """
        Get information about teacher with given code or tg user id, only one of parameters is required:

        - **code**: unique code, all teachers have this code
        - **tg_user_id**: unique telegram user id
    """
    try:
        db_sess = db_session.create_session()

        if not (body.code is None):
            code = body.code
            teacher = db_sess.query(Teacher).filter(Teacher.code == code).first()

            if teacher is None:
                raise TeacherNotFoundError(teacher_code=code)

            response_body = json_body.Teacher(
                name=teacher.name,
                surname=teacher.surname,
                patronymic=teacher.patronymic,
                class_name=teacher.class_name,
                school_name=teacher.school_name
            )

            if not (teacher.tg_user_id is None):
                response_body.tg_user_id = teacher.tg_user_id

            return response_body

        if not (body.tg_user_id is None):
            tg_user_id = body.tg_user_id

            teacher = db_sess.query(Teacher).filter(Teacher.tg_user_id == tg_user_id).first()

            if teacher is None:
                raise TeacherNotFoundError(teacher_tg_user_id=tg_user_id)

            response_body = json_body.Teacher(
                name=teacher.name,
                surname=teacher.surname,
                patronymic=teacher.patronymic,
                class_name=teacher.class_name,
                school_name=teacher.school_name,
                tg_user_id=teacher.tg_user_id
            )

            return response_body

    except (TeacherNotFoundError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return Response(content=str(error), status_code=status.HTTP_400_BAD_REQUEST)