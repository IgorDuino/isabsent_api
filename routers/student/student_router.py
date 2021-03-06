import base64
import logging
import routers.models as schemas

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from tools.error_book import *
from data import db_session
from tools.settings import *
from routers.responses import *
from data.student import Student
from data.absent import Absent
from tools.tools import generate_unique_code
from google_spreadsheets.google_spread_sheets import google_spread_sheets


student_router = APIRouter()


@student_router.put('/student/absent',
                    summary='Add student absent',
                    status_code=status.HTTP_201_CREATED,
                    responses={201: {"model": CreatedResponse, "description": "Absent has been added"},
                               400: {"model": BadRequest},
                               404: {"model": NotFound}})
def student_absent_put(body: schemas.Absent, code: str = None, tg_user_id: int = None):
    """
        Add student absent in db and google spreadsheets

        ### Query (_only one parameter required_):
        - **code**: unique code, all students have this code
        - **tg_user_id**: unique telegram user id
        ### Body:
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

        if not (code is None):
            student_code = code
            student = db_sess.query(Student).filter(Student.code == student_code).first()

            if student is None:
                raise StudentNotFoundError(student_code=student_code)

            student_id = student.id
            school = student.school
            link = school.link

        elif not (tg_user_id is None):
            tg_user_id = tg_user_id
            student = db_sess.query(Student).filter(Student.tg_user_id == tg_user_id).first()

            if student is None:
                raise StudentNotFoundError(student_tg_user_id=tg_user_id)

            student_id = student.id
            school = student.school
            link = school.link
        else:
            raise RequestDataKeysError([], ['code', 'tg_user_id'])

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

        return JSONResponse(**CreatedResponse(content='Absent added').dict())

    except (StudentDuplicateAbsent, RequestDataKeysError, ValueError) as error:
        logging.warning(error)
        return JSONResponse(**BadRequest(content=str(error)).dict())
    except StudentNotFoundError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())


@student_router.get('/student/absents',
                    summary='Get student absent list',
                    status_code=status.HTTP_200_OK,
                    responses={200: {"model": schemas.AbsentGetList, "description": "Successful Response"},
                               400: {"model": BadRequest},
                               404: {"model": NotFound}})
def student_absent_get(code: str = None, tg_user_id: int = None):
    """
        Get student absents by code or tg user id

        ### Query (_only one parameter required_):
        - **code**: unique code, all students have this code
        - **tg_user_id**: unique telegram user id
    """
    try:
        db_sess = db_session.create_session()

        if not (code is None):
            student = db_sess.query(Student).filter(Student.code == code).first()

            if student is None:
                raise StudentNotFoundError(student_code=code)
        elif not (tg_user_id is None):
            student = db_sess.query(Student).filter(Student.tg_user_id == tg_user_id).first()

            if student is None:
                raise StudentNotFoundError(student_tg_user_id=tg_user_id)
        else:
            raise RequestDataKeysError([], ['code', 'tg_user_id'])

        absent_list = schemas.AbsentGetList(absents=[])
        for absent in student.absents:
            absent = schemas.AbsentGet(
                date=datetime.date.strftime(absent.date, string_date_format),
                reason=absent.reason,
                code=student.code
            )

            if not (absent.file is None):
                absent.file = str(absent.file)

            absent_list.absents.append(absent)

        return JSONResponse(content=absent_list.dict(), status_code=status.HTTP_200_OK)

    except RequestDataKeysError as error:
        logging.warning(error)
        return JSONResponse(**BadRequest(content=str(error)).dict())
    except StudentNotFoundError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())


@student_router.patch('/student/absent',
                      summary='Change absent',
                      status_code=status.HTTP_200_OK,
                      responses={200: {"model": schemas.Absent},
                                 400: {"model": BadRequest},
                                 404: {"model": NotFound}})
def student_absent_patch(body: schemas.AbsentPatch, date: str, code: str = None, tg_user_id: int = None):
    """
        Change student absent in given date by code or tg user id

        ### Query (_only one parameter required_):
        - **code**: unique code, all students have this code
        - **tg_user_id**: unique telegram user id
        - **date**: absent date

        ### Body:
        - **new_date**: new date for absent, not required
        - **new_reason**: new reason for absent, not required
        - **new_file**: new file for absent, not required
    """
    try:
        db_sess = db_session.create_session()

        if not (code is None):
            student = db_sess.query(Student).filter(Student.code == code).first()

            if student is None:
                raise StudentNotFoundError(student_code=code)

        elif not (tg_user_id is None):
            student = db_sess.query(Student).filter(Student.tg_user_id == tg_user_id).first()

            if student is None:
                raise StudentNotFoundError(student_tg_user_id=tg_user_id)
        else:
            raise RequestDataKeysError([], ['code', 'tg_user_id'])

        school = student.school
        code = student.code
        for absent in student.absents:
            if absent.date == datetime.datetime.strptime(date, string_date_format):
                if body.new_reason:
                    absent.reason = body.new_reason
                if body.new_date:
                    absent.date = body.new_date
                if body.new_file:
                    absent.file = body.new_file
                break

        return JSONResponse(**SuccessfulResponse(content='Absent Changed').dict())
    except RequestDataKeysError as error:
        logging.warning(error)
        return JSONResponse(**BadRequest(content=str(error)).dict())
    except StudentNotFoundError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())


@student_router.post('/student/tg_auth',
                     summary='',
                     status_code=status.HTTP_200_OK,
                     responses={200: {"model": SuccessfulResponse, "description": "Tg user id has been bind"},
                                400: {"model": BadRequest},
                                404: {"model": NotFound}})
def student_tg_auth(body: schemas.TgAuth):
    """
        Binding telegram user id to student code

        ### Body (_all parameters required_):
        - **code**: unique code, all students have this code
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

        return JSONResponse(**SuccessfulResponse(content='Tg user id has been bind').dict())
    except StudentDuplicateTgUserIdError as error:
        logging.warning(error)
        return JSONResponse(**BadRequest(content=str(error)).dict())
    except StudentNotFoundError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())


@student_router.post('/student/code',
                     summary='Generating new code for student',
                     status_code=status.HTTP_200_OK,
                     responses={200: {"model": SuccessfulResponse, "description": "New code generate success"},
                                400: {"model": BadRequest},
                                404: {"model": NotFound}})
def student_pass(body: schemas.CodeTgUserId):
    """
        Generating new code for student with given code or telegram id

         ### Body (_only one parameter required_):
        - **code**: unique code, all students have this code
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

        else:
            raise RequestDataKeysError([], ['code', 'tg_user_id'])

        db_sess.commit()

        google_spread_sheets.google_sheets_student_code_generate(link, old_code, gen_code)

        return JSONResponse(**SuccessfulResponse(content='New code generate success').dict())
    except RequestDataKeysError as error:
        logging.warning(error)
        return JSONResponse(**BadRequest(content=str(error)).dict())
    except StudentNotFoundError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())


@student_router.get('/student',
                    summary='Get information about student',
                    status_code=status.HTTP_200_OK,
                    response_model=schemas.StudentGet,
                    responses={200: {"model": schemas.StudentGet},
                               400: {"model": BadRequest},
                               404: {"model": NotFound}})
def student_get(code: str = None, tg_user_id: int = None):
    """
        Get information about student with given code or tg user id

         ### Query (_only one parameter required_):
        - **code**: unique code, all students have this code
        - **tg_user_id**: unique telegram user id
    """
    try:
        db_sess = db_session.create_session()
        if not (code is None):
            student = db_sess.query(Student).filter(Student.code == code).first()

            if student is None:
                raise StudentNotFoundError(student_code=code)

            response_body = schemas.StudentGet(
                name=student.name,
                surname=student.surname,
                patronymic=student.patronymic,
                class_name=student.class_name,
                school_name=student.school_name,
                code=code
            )

            if not (student.tg_user_id is None):
                response_body.tg_user_id = student.tg_user_id

            return JSONResponse(content=response_body.dict(), status_code=status.HTTP_200_OK)

        elif not (tg_user_id is None):
            student = db_sess.query(Student).filter(Student.tg_user_id == tg_user_id).first()

            if student is None:
                raise StudentNotFoundError(student_tg_user_id=tg_user_id)

            response_body = schemas.StudentGet(
                name=student.name,
                surname=student.surname,
                patronymic=student.patronymic,
                class_name=student.class_name,
                school_name=student.school_name,
                code=student.code,
                tg_user_id=tg_user_id
            )

            return JSONResponse(content=response_body.dict(), status_code=status.HTTP_200_OK)

        else:
            raise RequestDataKeysError([], ['code', 'tg_user_id'])

    except RequestDataKeysError as error:
        logging.warning(error)
        return JSONResponse(**BadRequest(content=str(error)).dict())
    except StudentNotFoundError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())


@student_router.delete('/student',
                       summary='Delete student',
                       status_code=status.HTTP_200_OK,
                       responses={200: {"model": schemas.StudentGet},
                                  400: {"model": BadRequest},
                                  404: {"model": NotFound}})
def student_delete(code: str = None, tg_user_id: int = None, absents: bool = False):
    """
        Delete student with given code or tg user id

         ### Query:
        - **code**: unique code, all students have this code
        - **tg_user_id**: unique telegram user id
        - **absents**: flag, when true absents from given student will delete, not required
    """
    try:
        db_sess = db_session.create_session()
        if not (code is None):
            student = db_sess.query(Student).filter(Student.code == code).first()
        elif not (tg_user_id is None):
            student = db_sess.query(Student).filter(Student.tg_user_id == tg_user_id).first()
        else:
            raise RequestDataKeysError([], ['code', 'tg_user_id'])

        if student is None:
            raise StudentNotFoundError(student_code=code)

        if absents:
            for absent in student.absents:
                db_sess.delete(absent)

        db_sess.delete(student)
        db_sess.commit()

        return JSONResponse(**SuccessfulResponse(content='Student deleted').dict())

    except RequestDataKeysError as error:
        logging.warning(error)
        return JSONResponse(**BadRequest(content=str(error)).dict())
    except StudentNotFoundError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())


@student_router.patch('/student',
                      summary='Patch student',
                      status_code=status.HTTP_200_OK,
                      responses={200: {"model": schemas.StudentGet},
                                 400: {"model": BadRequest},
                                 404: {"model": NotFound}})
def student_patch(body: schemas.StudentPatch, code: str = None, tg_user_id: int = None):
    """
        Patch student with given code or tg user id

         ### Query (_only one parameter required_):
        - **code**: unique code, all students have this code
        - **tg_user_id**: unique telegram user id

        ### Body:
        - **new_name**: new name for student, not required
        - **new_surname**: new surname for student, not required
        - **new_patronymic**: new patronymic for student, not required
        - **new_class_name**: new class name for student, not required
        - **new_school_name**: new school name for student, not required
    """
    try:
        db_sess = db_session.create_session()

        if not (code is None):
            student = db_sess.query(Student).filter(Student.code == code).first()
        elif not (tg_user_id is None):
            student = db_sess.query(Student).filter(Student.tg_user_id == tg_user_id).first()
        else:
            raise RequestDataKeysError([], ['code', 'tg_user_id'])

        if student is None:
            raise StudentNotFoundError(student_code=code, student_tg_user_id=tg_user_id)

        if body.new_name:
            student.name = body.new_name
        if body.new_surname:
            student.surname = body.new_surname
        if body.new_patronymic:
            student.patronymic = body.new_patronymic
        if body.new_class_name:
            student.class_name = body.new_class_name
        if body.new_school_name:
            student.school_name = body.new_school_name

        db_sess.commit()

        return JSONResponse(**SuccessfulResponse(content='Student changed').dict())
    except RequestDataKeysError as error:
        logging.warning(error)
        return JSONResponse(**BadRequest(content=str(error)).dict())
    except StudentNotFoundError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())
