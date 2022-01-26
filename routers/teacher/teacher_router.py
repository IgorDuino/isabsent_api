import logging


from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from data.student import Student
from tools.error_book import *
from data import db_session
from data.teacher import Teacher
from tools.tools import generate_unique_code, find_student
from google_spreadsheets.google_spread_sheets import google_spread_sheets
import routers.models as schemas


teacher_router = APIRouter()


@teacher_router.post("/teacher/tg_auth",
                     summary='Binding tg user id to teacher code',
                     status_code=status.HTTP_201_CREATED,
                     responses={201: {"model": schemas.OkResponse, "description": "Tg user id has been bind"},
                                400: {"model": schemas.BadResponse}})
def teacher_tg_auth(body: schemas.TgAuth):
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

        return JSONResponse(content=schemas.OkResponse(msg='HTTP 201 CREATED').dict(),
                            status_code=status.HTTP_201_CREATED)
    except (TeacherDuplicateTgUserIdError, TeacherNotFoundError, RequestDataKeysError, RequestDataMissedKeyError,
            RequestDataTypeError) as error:
        logging.warning(error)
        return JSONResponse(content=schemas.BadResponse(error_msg=str(error)).dict(),
                            status_code=status.HTTP_400_BAD_REQUEST)


@teacher_router.post('/teacher/code',
                     summary='Generating new code for teacher',
                     status_code=status.HTTP_201_CREATED,
                     responses={201: {"model": schemas.OkResponse, "description": "New code generate success"},
                                400: {"model": schemas.BadResponse}})
def teacher_pass(body: schemas.CodeTgUserId):
    """
        Generating new code for teacher, only one of parameters is required:

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
        else:
            raise RequestDataKeysError([], ['code', 'tg_user_id'])

        db_sess.commit()

        google_spread_sheets.google_sheets_teacher_code_generate(link, old_code, gen_code)

        return JSONResponse(content=schemas.OkResponse(msg='HTTP 201 CREATED').dict(),
                            status_code=status.HTTP_201_CREATED)
    except (TeacherNotFoundError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return JSONResponse(content=schemas.BadResponse(error_msg=str(error)).dict(),
                            status_code=status.HTTP_400_BAD_REQUEST)


@teacher_router.get('/teacher',
                    summary='Get information about teacher',
                    status_code=status.HTTP_200_OK,
                    response_model=schemas.TeacherGet,
                    responses={200: {"model": schemas.TeacherGet, "description": "Successful Response"},
                               400: {"model": schemas.BadResponse}})
def teacher_get(code: str = None, tg_user_id: int = None):
    """
        Get information about teacher with given code or tg user id, only one of parameters is required:

        - **code**: unique code, all teachers have this code
        - **tg_user_id**: unique telegram user id
    """
    try:
        db_sess = db_session.create_session()

        if not (code is None):
            teacher = db_sess.query(Teacher).filter(Teacher.code == code).first()

            if teacher is None:
                raise TeacherNotFoundError(teacher_code=code)

            response_body = schemas.TeacherGet(
                name=teacher.name,
                surname=teacher.surname,
                patronymic=teacher.patronymic,
                class_name=teacher.class_name,
                school_name=teacher.school_name,
                code=code
            )

            if not (teacher.tg_user_id is None):
                response_body.tg_user_id = teacher.tg_user_id

            return JSONResponse(content=response_body.dict(), status_code=status.HTTP_200_OK)

        elif not (tg_user_id is None):
            teacher = db_sess.query(Teacher).filter(Teacher.tg_user_id == tg_user_id).first()

            if teacher is None:
                raise TeacherNotFoundError(teacher_tg_user_id=tg_user_id)

            response_body = schemas.TeacherGet(
                name=teacher.name,
                surname=teacher.surname,
                patronymic=teacher.patronymic,
                class_name=teacher.class_name,
                school_name=teacher.school_name,
                code=teacher.code,
                tg_user_id=tg_user_id
            )

            return JSONResponse(content=response_body.dict(), status_code=status.HTTP_200_OK)

        else:
            raise RequestDataKeysError([], ['code', 'tg_user_id'])

    except (TeacherNotFoundError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return JSONResponse(content=schemas.BadResponse(error_msg=str(error)).dict(),
                            status_code=status.HTTP_400_BAD_REQUEST)


@teacher_router.get('/teacher/students_by_name',
                    summary='Get students by name',
                    status_code=status.HTTP_200_OK,
                    responses={200: {"model": schemas.FindByNameResponse, "description": "Successful Response"},
                               400: {"model": schemas.BadResponse}})
def teacher_get_student_by_name(name: str, code: str = None, tg_user_id: int = None):
    """
        Get information about teacher students with given name:

        - **code**: unique code, all teachers have this code, not required
        - **tg_user_id**: unique telegram user id, not required
        - **name**: student name, required
    """
    try:
        db_sess = db_session.create_session()
        teacher = None

        if not (code is None):
            teacher = db_sess.query(Teacher).filter(Teacher.code == code).first()

            if teacher is None:
                raise TeacherNotFoundError(teacher_code=code)

        elif not (tg_user_id is None):
            teacher = db_sess.query(Teacher).filter(Teacher.tg_user_id == tg_user_id).first()

            if teacher is None:
                raise TeacherNotFoundError(teacher_tg_user_id=tg_user_id)

        else:
            raise RequestDataKeysError([], ['code', 'tg_user_id'])

        student_list = []
        for student in teacher.students:
            student_list.append((f'{student.surname} {student.name} {student.patronymic}', student.code))

        response_list = find_student(student_list, name)

        response_json = schemas.FindByNameResponse(students=[])
        for code in response_list:
            student = db_sess.query(Student).filter(Student.code == code).first()
            student_json = schemas.StudentGet(
                name=student.name,
                surname=student.surname,
                patronymic=student.patronymic,
                class_name=student.class_name,
                school_name=student.school_name,
                code=student.code
            )
            if not (student.tg_user_id is None):
                student_json.tg_user_id = student.tg_user_id

            response_json.students.append(student_json)
        return JSONResponse(content=response_json.dict(), status_code=status.HTTP_200_OK)

    except (TeacherNotFoundError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return JSONResponse(content=schemas.BadResponse(error_msg=str(error)).dict(),
                            status_code=status.HTTP_400_BAD_REQUEST)


@teacher_router.get('/teacher/students',
                    summary='Get students by name',
                    status_code=status.HTTP_200_OK,
                    responses={200: {"model": schemas.StudentListGet, "description": "Successful Response"},
                               400: {"model": schemas.BadResponse}})
def teacher_get_student_by_name(code: str = None, tg_user_id: int = None):
    """
        Get information about teacher students with given code or tg user id:

        - **code**: unique code, all teachers have this code, not required
        - **tg_user_id**: unique telegram user id, not required
    """
    try:
        db_sess = db_session.create_session()
        teacher = None

        if not (code is None):
            teacher = db_sess.query(Teacher).filter(Teacher.code == code).first()

            if teacher is None:
                raise TeacherNotFoundError(teacher_code=code)

        elif not (tg_user_id is None):
            teacher = db_sess.query(Teacher).filter(Teacher.tg_user_id == tg_user_id).first()

            if teacher is None:
                raise TeacherNotFoundError(teacher_tg_user_id=tg_user_id)

        else:
            raise RequestDataKeysError([], ['code', 'tg_user_id'])

        student_list = schemas.StudentListGet(students=[])
        for student in teacher.students:
            student_list.students.append(
                schemas.StudentGet(name=student.name,
                                   surname=student.surname,
                                   patronymic=student.patronymic,
                                   class_name=student.class_name,
                                   school_name=student.school_name,
                                   code=student.code,
                                   tg_user_id=student.tg_user_id))

        return JSONResponse(content=student_list.dict(), status_code=status.HTTP_200_OK)

    except (TeacherNotFoundError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return JSONResponse(content=schemas.BadResponse(error_msg=str(error)).dict(),
                            status_code=status.HTTP_400_BAD_REQUEST)


@teacher_router.get('/teacher/absents',
                    summary='Get teacher`s student absent list',
                    status_code=status.HTTP_200_OK,
                    responses={200: {"model": schemas.AbsentList, "description": "Successful Response"},
                               400: {"model": schemas.BadResponse}})
def teacher_students_absents(date: str, code: str = None, tg_user_id: int = None):
    """
        Get student absent from teacher with given code or tg user id:

        - **code**: unique code, all teachers have this code, not required
        - **tg_user_id**: unique telegram user id, not required
        - **date**: absent date, required
    """
    try:
        db_sess = db_session.create_session()
        response_dict = schemas.AbsentList(absents=[])
        if not (code is None):
            teacher = db_sess.query(Teacher).filter(Teacher.code == code).first()
            if teacher is None:
                raise TeacherNotFoundError(teacher_code=code)

            for student in teacher.students:
                for absent in student.absents:
                    if date is None:
                        response_dict.absents.append(schemas.Absent(
                            date=absent.date.isoformat(),
                            reason=absent.reason,
                            code=student.code
                        ))
                        continue

                    if absent.date.isoformat() == date:
                        response_dict.absents.append(schemas.Absent(
                            date=absent.date.isoformat(),
                            reason=absent.reason,
                            code=student.code,
                        ))

        elif not (tg_user_id is None):
            teacher = db_sess.query(Teacher).filter(Teacher.tg_user_id == tg_user_id).first()
            if teacher is None:
                raise TeacherNotFoundError(teacher_tg_user_id=tg_user_id)

            for student in teacher.students:
                for absent in student.absents:
                    if date is None:
                        response_dict.absents.append(schemas.Absent(
                            date=absent.date,
                            reason=absent.reason,
                            code=student.code,
                        ))
                        continue

                    if absent.date.isoformat() == date:
                        response_dict.absents.append(schemas.Absent(
                            date=absent.date.isoformat(),
                            reason=absent.reason,
                            code=student.code,
                        ))
        else:
            raise RequestDataKeysError([], ['code', 'tg_user_id'])

        return JSONResponse(content=response_dict.dict(), status_code=status.HTTP_200_OK)
    except (TeacherNotFoundError, RequestDataKeysError, RequestDataMissedKeyError, RequestDataTypeError) as error:
        logging.warning(error)
        return JSONResponse(content=schemas.BadResponse(error_msg=str(error)).dict(),
                            status_code=status.HTTP_400_BAD_REQUEST)