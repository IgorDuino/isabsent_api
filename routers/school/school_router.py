import logging
import routers.models as schemas

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from tools.error_book import *
from data import db_session
from data.school import School
from data.teacher import Teacher
from data.student import Student
from routers.responses import *
from tools.settings import string_date_format
from tools.tools import generate_unique_code
from google_spreadsheets.google_spread_sheets import google_spread_sheets


school_router = APIRouter()


@school_router.put('/school',
                   summary='Add new school',
                   status_code=status.HTTP_201_CREATED,
                   responses={201: {"model": CreatedResponse, "description": "School has been added"},
                              400: {"model": BadRequest}})
def school_put(body: schemas.School):
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

        return JSONResponse(**CreatedResponse(content='School created').dict())
    except SchoolDuplicateError as error:
        logging.warning(error)
        return JSONResponse(**BadRequest(content=str(error)).dict())


@school_router.get('/school',
                   summary='Get information about school',
                   status_code=status.HTTP_200_OK,
                   responses={200: {"model": schemas.School},
                              400: {"model": BadRequest}})
def school_get(name: str):
    """
        Get information about school by name:

        - **school_name**: school name, required
    """
    try:
        db_sess = db_session.create_session()

        school = db_sess.query(School).get(name)
        if school is None:
            raise SchoolNotFoundError(name)

        return JSONResponse(content=schemas.School(school_name=name, link=school.link).dict(),
                            status_code=status.HTTP_200_OK)
    except SchoolNotFoundError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())


@school_router.get('/schools',
                   summary='Get school list',
                   status_code=status.HTTP_200_OK,
                   responses={200: {"model": schemas.SchoolList},
                              400: {"model": BadRequest}})
def schools_get():
    """
        Get school list, no parameters need
    """
    try:
        db_sess = db_session.create_session()

        school_list = db_sess.query(School).all()

        response_dict = schemas.SchoolList(schools=[])
        for school in school_list:
            response_dict.schools.append(schemas.School(school_name=school.name, link=school.link))

        return JSONResponse(content=response_dict.dict(), status_code=status.HTTP_200_OK)
    except SchoolDuplicateError as error:
        logging.warning(error)
        return JSONResponse(**BadRequest(content=str(error)).dict())


@school_router.put('/school/teachers',
                   summary='Add list of teachers',
                   status_code=status.HTTP_201_CREATED,
                   responses={201: {"model": CreatedResponse, "description": "Teachers has been added"},
                              400: {"model": BadRequest},
                              404: {"model": NotFound}})
def teachers_put(body: schemas.TeacherListPost):
    """
        Add teacher list to given school:

        - **school_name**: school name, required
        - **teachers**: list of teachers, not required, if not given, teachers will take from Google spreadsheets
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
                **teacher_json,
                school_name=school_name,
                code=code
            ))

            teacher_code_list.append([code])

        db_sess.add_all(teacher_list)
        db_sess.commit()

        if from_sheet_flag:
            link = school.link
            google_spread_sheets.google_sheets_teachers_codes(link, teacher_code_list)

        return JSONResponse(**CreatedResponse(content='Teachers added').dict())
    except StudentNotFoundError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())
    except TeachersEmptyData as error:
        logging.warning(error)
        return JSONResponse(**BadRequest(content=str(error)).dict())


@school_router.get('/school/teachers',
                   summary='Get list of teachers',
                   status_code=status.HTTP_200_OK,
                   responses={200: {"model": schemas.TeacherListGet},
                              400: {"model": BadRequest},
                              404: {"model": NotFound}})
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

        teacher_dict_list = schemas.TeacherListGet(teachers=[])
        for teacher in teacher_list:
            response = schemas.TeacherGet(
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
    except SchoolNotFoundError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())


@school_router.get('/school/absents',
                   summary='Get list of absents',
                   status_code=status.HTTP_200_OK,
                   responses={200: {"model": schemas.AbsentList},
                              400: {"model": BadRequest},
                              404: {"model": NotFound}})
def absents_get(school_name: str):
    """
       Get absent list from given school:

       - **school_name**: school name, required
   """
    try:
        db_sess = db_session.create_session()

        school = db_sess.query(School).get(school_name)
        if school is None:
            raise SchoolNotFoundError(school_name)

        students = db_sess.query(Student).filter(Student.school_name == school_name).all()
        absents = []
        for student in students:
            absents += student.absents

        absent_json_list = schemas.AbsentList(absents=[])
        for absent in absents:
            student = absent.student
            absent_json = schemas.Absent(
                date=datetime.date.strftime(absent.date, string_date_format),
                reason=absent.reason,
                code=student.code,
                tg_user_id=student.tg_user_id
            )

            if not (absent.file is None):
                absent_json.file = str(absent.file)

            absent_json_list.absents.append(absent_json)

        return JSONResponse(content=absent_json_list.dict(), status_code=status.HTTP_200_OK)
    except SchoolNotFoundError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())


@school_router.put('/school/students',
                   summary='Add list of students',
                   status_code=status.HTTP_201_CREATED,
                   responses={201: {"model": CreatedResponse, "description": "Students has been added"},
                              400: {"model": BadRequest},
                              404: {"model": NotFound}})
def students_put(body: schemas.StudentListPost):
    """
        Add student list to given school:

        - **school_name**: school name, required
        - **teachers**: list of students, not required, if not given, teachers will take from Google spreadsheets
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
                **student_json,
                school_name=school_name,
                code=code
            ))

            student_code_list.append([code])

        db_sess.add_all(student_list)
        db_sess.commit()

        if from_sheet_flag:
            link = school.link
            google_spread_sheets.google_sheets_students_codes(link, student_code_list)

        return JSONResponse(**BadRequest(content='Students added').dict())
    except SchoolNotFoundError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())
    except StudentsEmptyData as error:
        logging.warning(error)
        return JSONResponse(**BadRequest(content=str(error)).dict())


@school_router.get('/school/students',
                   summary='Get list of students',
                   status_code=status.HTTP_200_OK,
                   responses={200: {"model": schemas.StudentListGet, "description": "Success response"},
                              400: {"model": BadRequest},
                              404: {"model": NotFound}})
def students_get(school_name: str):
    """
        Get student list from given school:

        - **school_name**: school name, required
    """
    try:
        db_sess = db_session.create_session()

        school = db_sess.query(School).get(school_name)
        if school is None:
            SchoolNotFoundError(school_name)

        student_list = db_sess.query(Student).filter(Student.school_name == school_name).all()

        student_dict_list = schemas.StudentListGet(students=[])
        for student in student_list:
            student_dict = schemas.StudentGet(
                name=student.name,
                surname=student.surname,
                patronymic=student.patronymic,
                class_name=student.class_name,
                school_name=student.school_name,
                code=student.code
            )

            if not (student.tg_user_id is None):
                student_dict.tg_user_id = student.tg_user_id

            student_dict_list.students.append(student_dict)

        return JSONResponse(content=student_dict_list.dict(), status_code=status.HTTP_200_OK)
    except SchoolNotFoundError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())


@school_router.get('/school/find_by_code',
                   summary='Get information about teacher',
                   status_code=status.HTTP_200_OK,
                   responses={200: {"model": schemas.StudentTeacher},
                              400: {"model": BadRequest},
                              404: {"model": NotFound}})
def find_by_code(code: str = None, tg_user_id: int = None):
    """
        Get information about teacher or student with given code or tg user id, only one of parameters is required:

        - **code**: unique code, all teachers have this code
        - **tg_user_id**: unique telegram user id
    """
    try:
        db_sess = db_session.create_session()

        if not (code is None):
            teacher = db_sess.query(Teacher).filter(Teacher.code == code).first()
            student = db_sess.query(Student).filter(Student.code == code).first()

            if not (teacher is None):
                response_body = schemas.StudentTeacher(
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
                response_body = schemas.StudentTeacher(
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
                response_body = schemas.StudentTeacher(
                    name=teacher.name,
                    surname=teacher.surname,
                    patronymic=teacher.patronymic,
                    class_name=teacher.class_name,
                    school_name=teacher.school_name,
                    tg_user_id=teacher.tg_user_id,
                    type='teacher'
                )

            elif not (student is None):
                response_body = schemas.StudentTeacher(
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

    except RequestDataKeysError as error:
        logging.warning(error)
        return JSONResponse(**BadRequest(content=str(error)).dict())
    except StudentTeacherNotFoundError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())


@school_router.delete('/school',
                      summary='Delete school',
                      status_code=status.HTTP_200_OK,
                      responses={200: {"model": SuccessfulResponse},
                                 400: {"model": BadRequest},
                                 404: {"model": NotFound}})
def school_del(name: str, teachers: bool = False, students: bool = False, absents: bool = False):
    """
        Delete school with given name:

        - **name**: unique school name, required
        - **teachers**: flag when true teachers from given school will delete, not required
        - **students**: flag when true students from given school will delete, not required
        - **absents**: flag when true students from given school will delete, not required
    """
    try:
        db_sess = db_session.create_session()
        school = db_sess.query(School).get(name)

        if school is None:
            raise SchoolNotFoundError(school_name=name)

        if teachers:
            for teacher in school.teachers:
                db_sess.delete(teacher)

        if students:
            for student in school.students:
                if absents:
                    for absent in student.absents:
                        db_sess.delete(absent)
                db_sess.delete(student)

        db_sess.delete(school)
        db_sess.commit()
        return JSONResponse(**SuccessfulResponse(content='School deleted').dict())
    except SchoolNotFoundError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())


@school_router.patch('/school',
                     summary='Patch school',
                     status_code=status.HTTP_200_OK,
                     responses={200: {"model": SuccessfulResponse},
                                400: {"model": BadRequest},
                                404: {"model": NotFound}})
def school_patch(name: str, body: schemas.SchoolPatch):
    """
        Change school with given name:

        - **new_name**: new school name, not required
        - **new_link**: new link name, not required
    """
    try:
        db_sess = db_session.create_session()
        school = db_sess.query(School).get(name)

        if school is None:
            raise SchoolNotFoundError(school_name=name)

        if body.new_name:
            school.school_name = body.new_name

        if body.new_link:
            school.link = body.new_link

        db_sess.commit()
        return JSONResponse(**SuccessfulResponse(content='School changed').dict())
    except SchoolNotFoundError as error:
        logging.warning(error)
        return JSONResponse(**NotFound(content=str(error)).dict())
