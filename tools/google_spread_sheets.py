import json
import gspread
import datetime

gc = gspread.service_account(filename='google_credentials.json')


def google_sheets_teachers_codes(link: str, code_list: list):
    """Adding teachers codes into google sheet"""
    pass


def google_sheets_teacher_code_generate(link: str, code: str):
    """Changing teacher code to generate one"""
    pass


def google_sheets_students_codes(link: str, code_list: list):
    """Adding students codes into google sheet"""
    pass


def google_sheets_student_code_generate(link: str, code: str):
    """Changing student code to generate one"""
    pass


def google_sheets_student_absent(link: str, date: datetime.date, reason: str,
                                 name: str, surname: str, patronymic: str, class_name: str):
    """Adding student absent into google sheet"""
    table = gc.open_by_url(link)
    worksheet = table.add_worksheet(title=str(date), rows=10, cols=10)
    worksheet.update('A1', [[reason, name]])


google_sheets_student_absent(
    'https://docs.google.com/spreadsheets/d/1UPO9M6_fOwzSQmmasYmnxMnSEtCiq9LC4qf3300YzEc/edit#gid=1955592902',
    datetime.date.today, 'бо')
