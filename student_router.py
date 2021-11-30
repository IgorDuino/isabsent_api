import base64
import logging

from fastapi import APIRouter, Response, status
from tools.error_book import *
from data import db_session
from tools.settings import *
from data.student import Student
from data.absent import Absent
from tools.tools import generate_unique_code
from google_spreadsheets.google_spread_sheets import google_spread_sheets
import tools.models as json_body


student_router = APIRouter()


@student_router.post('/student/absent',
                     summary='Add student absent',
                     status_code=status.HTTP_201_CREATED)
def student_absent(body: json_body.StudentAbsent):
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

        return Response(content='HTTP_201_CREATED', status_code=status.HTTP_201_CREATED)

    except (StudentDuplicateAbsent, StudentNotFoundError, RequestDataKeysError, RequestDataMissedKeyError,
            RequestDataTypeError) as error:
        logging.warning(error)
        return Response(content=str(error), status_code=status.HTTP_400_BAD_REQUEST)


@student_router.get('/student/absent',
                     summary='Get student absent list',
                     status_code=status.HTTP_201_CREATED)
def student_absent(body: json_body.StudentCodeTgUserId):
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
                "date": absent.date,
                "reason": absent.reason,
            }

            if not (absent.file is None):
                absent_json['file'] = str(absent.file)

            absent_list.absents.append(absent_json)

        return absent_list

    except (StudentDuplicateAbsent, StudentNotFoundError, RequestDataKeysError, RequestDataMissedKeyError,
            RequestDataTypeError) as error:
        logging.warning(error)
        return Response(content=str(error), status_code=status.HTTP_400_BAD_REQUEST)
