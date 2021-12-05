import gspread

from tools.error_book import *


class GoogleSpreadSheetsApi:
    def __init__(self, file_name):
        self.gc = gspread.service_account(filename=file_name)

    @staticmethod
    def style_new_worksheet(worksheet):
        worksheet.format('1:1000', {'textFormat': {"fontSize": 12}})
        worksheet.format('1:1', {'textFormat': {"fontSize": 14, 'bold': True}})
        worksheet.append_row(['Класс', 'Фамилия', 'Имя', 'Отчество', 'Причина', 'Доказательства'])

    def google_sheets_teachers_codes(self, link: str, code_list: list):
        """Adding teachers codes into google sheet"""
        table = self.gc.open_by_url(link)
        worksheet = table.get_worksheet(0)

        cell_range = f'E2:E{len(code_list) + 1}'

        worksheet.update(cell_range, code_list)

    def google_sheets_teacher_code_generate(self, link: str, old_code: str, code: str):
        """Changing teacher code to generate one"""
        table = self.gc.open_by_url(link)
        worksheet = table.get_worksheet(0)
        cell: gspread.Cell = worksheet.find(old_code)

        if cell is None:
            raise TeacherNotFoundError(teacher_code=old_code, google_spread_sheet_link=link)

        worksheet.update(cell.address, code)

    def google_sheets_get_teachers(self, link: str, school: str):
        """Getting teachers list"""
        table = self.gc.open_by_url(link)
        worksheet = table.get_worksheet(0)
        data = worksheet.get_all_values()

        if len(data) < 1:
            raise TeachersEmptyData(link, school)

        data = data[1:]

        teachers_list = []

        for student in data:
            teachers_list.append(
                {
                    'name': student[2],
                    'surname': student[1],
                    'patronymic': student[3],
                    'class_name': student[0]
                }
            )

        return teachers_list

    def google_sheets_students_codes(self, link: str, code_list: list):
        """Adding students codes into google sheet"""
        table = self.gc.open_by_url(link)
        worksheet = table.get_worksheet(1)

        cell_range = f'E2:E{len(code_list) + 1}'

        worksheet.update(cell_range, code_list)

    def google_sheets_student_code_generate(self, link: str, old_code: str, code: str):
        """Changing student code to generate one"""
        table = self.gc.open_by_url(link)
        worksheet = table.get_worksheet(1)
        cell: gspread.Cell = worksheet.find(old_code)

        if cell is None:
            raise StudentNotFoundError(teacher_code=old_code, google_spread_sheet_link=link)

        worksheet.update(cell.address, code)

    def google_sheets_get_students(self, link: str, school: str):
        """Getting students list"""
        table = self.gc.open_by_url(link)
        worksheet = table.get_worksheet(1)
        data = worksheet.get_all_values()

        if len(data) < 1:
            raise StudentsEmptyData(link, school)

        data = data[1:]

        student_list = []

        for student in data:
            student_list.append(
                {
                    'name': student[2],
                    'surname': student[1],
                    'patronymic': student[3],
                    'class_name': student[0]
                }
            )

        return student_list

    def google_sheets_student_absent(self, link: str, date: datetime.date, reason: str,
                                     name: str, surname: str, patronymic: str, class_name: str, proof: bytes = ''):
        """Adding student absent into google sheet"""
        table = self.gc.open_by_url(link)
        for worksheet_elem in table.worksheets():
            if str(date) == worksheet_elem._properties['title']:
                worksheet = table.worksheet(str(date))
                break
        else:
            worksheet = table.add_worksheet(title=str(date), rows=1000, cols=6)
            self.style_new_worksheet(worksheet)

        worksheet.append_row([class_name, surname, name, patronymic, reason, proof])


google_spread_sheets = GoogleSpreadSheetsApi('google_spreadsheets/google_credentials.json')


# google_spread_sheets.google_sheets_student_absent(
#     'https://docs.google.com/spreadsheets/d/1UPO9M6_fOwzSQmmasYmnxMnSEtCiq9LC4qf3300YzEc/edit#gid=1955592902',
#     datetime.date.today(), 'болезнь', 'игорь', 'кузьменков', 'кириллович', '10-Г')
# google_spread_sheets.google_sheets_student_absent(
#     'https://docs.google.com/spreadsheets/d/1UPO9M6_fOwzSQmmasYmnxMnSEtCiq9LC4qf3300YzEc/edit#gid=1955592902',
#     datetime.date.today(), 'отсутствует', 'Кирилл', 'Кузьменков', 'Владимирович', '10-Г')
#
# google_spread_sheets.google_sheets_get_students(
#     'https://docs.google.com/spreadsheets/d/1UPO9M6_fOwzSQmmasYmnxMnSEtCiq9LC4qf3300YzEc/edit#gid=1955592902', '1580')
#
# google_spread_sheets.google_sheets_teacher_code_generate(
#     'https://docs.google.com/spreadsheets/d/1UPO9M6_fOwzSQmmasYmnxMnSEtCiq9LC4qf3300YzEc/edit#gid=1955592902', '120621',
#     '123456')
