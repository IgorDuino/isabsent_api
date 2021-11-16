import datetime


class RequestDataTypeError(Exception):
    """Exception raised when wrong type given in request data"""
    def __init__(self, key: str, right_type: type, wrong_type: type):
        self.key = key
        self.right_type = right_type
        self.wrong_type = wrong_type

    def __str__(self):
        return f'Wrong type in key {self.key}: must be {self.right_type}, get {self.wrong_type}'


class RequestDataKeysError(Exception):
    """Exception raised when wrong keys list given in request data"""
    def __init__(self, wrong_keys: list, right_keys: list):
        self.wrong_keys = wrong_keys
        self.right_keys = right_keys

    def __str__(self):
        return f'Wrong keys in request data: must be {self.right_keys}, get {self.wrong_keys}'


class RequestDataMissedKeyError(Exception):
    """Exception raised when missed key in request data"""
    def __init__(self, missed_key: str):
        self.missed_key = missed_key

    def __str__(self):
        return f'Missed key in request data {self.missed_key}'


class TeacherNotFoundError(Exception):
    """Exception raised when teacher with given in request data code not found"""
    def __init__(self, teacher_code: str):
        self.teacher_code = teacher_code

    def __str__(self):
        return f'Teacher with code: {self.teacher_code} not found'


class TeachersFromSchoolNotFoundError(Exception):
    """Exception raised when teacher with given in request data school_name not found"""
    def __init__(self, school_name: str):
        self.school_name = school_name

    def __str__(self):
        return f'Teachers with school name: {self.school_name} not found'


class TeacherDuplicateTgUserIdError(Exception):
    """Exception raised when teacher with given in request data tg_user_id is already exist"""
    def __init__(self, teacher_tg_user_id: int):
        self.teacher_tg_user_id = teacher_tg_user_id

    def __str__(self):
        return f'Teacher with tg id: {self.teacher_tg_user_id} is already exist'


class StudentNotFoundError(Exception):
    """Exception raised when student with given in request data code or tg_user_id not found"""
    def __init__(self, student_code: str = '', student_tg_user_id: int = -1):
        self.student_code = student_code
        self.student_tg_user_id = student_tg_user_id

    def __str__(self):
        if self.student_code != '':
            return f'Student with code: {self.student_code} not found'
        if self.student_tg_user_id != -1:
            return f'Student with tg_id: {self.student_tg_user_id} not found'


class StudentDuplicateTgUserIdError(Exception):
    """Exception raised when student with given in request data tg_user_id is already exist"""
    def __init__(self, student_tg_user_id: int):
        self.student_tg_user_id = student_tg_user_id

    def __str__(self):
        return f'Student with tg id: {self.student_tg_user_id} is already exist'


class StudentDuplicateAbsent(Exception):
    """Exception raised when student with given in request data code or tg_user_id is already absent"""
    def __init__(self, date: datetime.date, student_id: int):
        self.date = date
        self.student_id = student_id

    def __str__(self):
        return f'Student with id: {self.student_id} is already absent in {self.date.isoformat()}'


class SchoolNotFoundError(Exception):
    """Exception raised when school with given in request data code not found"""
    def __init__(self, school_name: int):
        self.school_name = school_name

    def __str__(self):
        return f'School with name: {self.school_name} not found'