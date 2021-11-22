import json
import gspread
import datetime
from gspread_formatting import *

gc = gspread.service_account(filename='google_credentials.json')


def style_new_worksheet(worksheet):
    worksheet.format('1:1000', {'textFormat': {"fontSize": 12}})
    worksheet.format('1:1', {'textFormat': {"fontSize": 14, 'bold': True}})
    worksheet.append_row(['Класс', 'Фамилия', 'Имя', 'Отчество', 'Причина', 'Докозательства'])


def google_sheets_teachers_codes(link: str, code_list: list):
    """Adding teachers codes into google sheet"""
    pass


def google_sheets_teacher_code_generate(link: str, old_code: str, code: str):
    """Changing teacher code to generate one"""
    table = gc.open_by_url(link)
    worksheet = table.get_worksheet(0)
    cell: gspread.Cell = worksheet.find(old_code)
    if cell is None:
        return
    cell.update(code)


def google_sheets_students_codes(link: str, code_list: list):
    """Adding students codes into google sheet"""
    pass


def google_sheets_student_code_generate(link: str, code: str):
    """Changing student code to generate one"""
    pass


def google_sheets_get_students(link: str, school: str):
    """Getting students list"""
    table = gc.open_by_url(link)
    worksheet = table.get_worksheet(1)
    data = worksheet.get_all_values()

    if len(data) < 1:
        return
    data = data[1:]

    a = {
        "school_name": school,
        "students": []
    }

    for student in data:
        a['students'].append(
            {
                'name': student[2],
                'surname': student[1],
                'patronymic': student[3],
                'class_name': student[0]
            }
        )

    return a


def google_sheets_get_teachers(link: str, school: str):
    """Getting teachers list"""
    table = gc.open_by_url(link)
    worksheet = table.get_worksheet(0)
    data = worksheet.get_all_values()

    if len(data) < 1:
        return
    data = data[1:]

    a = {
        "school_name": school,
        "teachers": []
    }

    for student in data:
        a['teachers'].append(
            {
                'name': student[2],
                'surname': student[1],
                'patronymic': student[3],
                'class_name': student[0]
            }
        )

    return a


def google_sheets_student_absent(link: str, date: datetime.date, reason: str,
                                 name: str, surname: str, patronymic: str, class_name: str):
    """Adding student absent into google sheet"""
    table = gc.open_by_url(link)
    for worksheet_elem in table.worksheets():
        if str(date) == worksheet_elem._properties['title']:
            worksheet = table.worksheet(str(date))
            break
    else:
        worksheet = table.add_worksheet(title=str(date), rows=1000, cols=6)
        style_new_worksheet(worksheet)

    worksheet.append_row([class_name, surname, name, patronymic, reason])


# google_sheets_student_absent(
#     'https://docs.google.com/spreadsheets/d/1UPO9M6_fOwzSQmmasYmnxMnSEtCiq9LC4qf3300YzEc/edit#gid=1955592902',
#     datetime.date.today(), 'болезнь', 'игорь', 'кузьменков', 'кириллович', '10-Г')
# google_sheets_student_absent(
#     'https://docs.google.com/spreadsheets/d/1UPO9M6_fOwzSQmmasYmnxMnSEtCiq9LC4qf3300YzEc/edit#gid=1955592902',
#     datetime.date.today(), 'отсутствует', 'Кирилл', 'Кузьменков', 'Владимирович', '10-Г')
#
# google_sheets_get_students(
#     'https://docs.google.com/spreadsheets/d/1UPO9M6_fOwzSQmmasYmnxMnSEtCiq9LC4qf3300YzEc/edit#gid=1955592902', '1580')

google_sheets_teacher_code_generate(
    'https://docs.google.com/spreadsheets/d/1UPO9M6_fOwzSQmmasYmnxMnSEtCiq9LC4qf3300YzEc/edit#gid=1955592902', '882352',
    '123456')
