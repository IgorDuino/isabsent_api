from .error_book import *


def key_type_validate(data: dict, keys_type_dict: dict) -> None:
    for key, item in keys_type_dict.items():
        if key not in data.keys():
            raise RequestDataMissedKeyError(key)
        if not isinstance(data[key], item):
            raise RequestDataTypeError(key, item, type(data[key]))

    if len(data.keys()) != len(keys_type_dict.keys()):
        raise RequestDataKeysError(list(data.keys()), list(keys_type_dict.keys()))


def teacher_post_validate(data: dict) -> None:
    keys_type_dict = {
        'name': str,
        'surname': str,
        'patronymic': str,
        'class_name': str,
        'school_name': str
    }

    key_type_validate(data, keys_type_dict)


def teacher_tg_auth_validate(data: dict) -> None:
    keys_type_dict = {
        "code": str,
        "tg_user_id": int
    }

    key_type_validate(data, keys_type_dict)


def teacher_gen_password_validate(data: dict) -> None:
    variable_key_type_dict = {
        'code': str,
        'tg_user_id': int
    }

    if ('code' not in data.keys()) and ('tg_user_id' not in data.keys()):
        raise RequestDataKeysError(list(data.keys()), list(variable_key_type_dict.keys()))

    if 'code' in data.keys() and type(data['code']) != variable_key_type_dict['code']:
        raise RequestDataTypeError('code', type(data['code']), variable_key_type_dict['code'])

    if 'tg_user_id' in data.keys() and type(data['tg_user_id']) != variable_key_type_dict['tg_user_id']:
        raise RequestDataTypeError('tg_user_id', type(data['tg_user_id']), variable_key_type_dict['tg_user_id'])


def teachers_post_validate(data: dict) -> None:
    keys_type_dict = {
        "teachers": list,
    }

    key_type_validate(data, keys_type_dict)


def teachers_get_validate(data: dict) -> None:
    keys_type_dict = {
        "school_name": str,
    }

    key_type_validate(data, keys_type_dict)


def student_post_validate(data: dict) -> None:
    keys_type_dict = {
        'name': str,
        'surname': str,
        'patronymic': str,
        'class_name': str,
        'school_name': str
    }

    key_type_validate(data, keys_type_dict)


def student_tg_auth_validate(data: dict) -> None:
    keys_type_dict = {
        "code": str,
        "tg_user_id": int
    }

    key_type_validate(data, keys_type_dict)


def student_gen_password_validate(data: dict) -> None:
    variable_key_type_dict = {
        'code': str,
        'tg_user_id': int
    }

    if ('code' not in data.keys()) and ('tg_user_id' not in data.keys()):
        raise RequestDataKeysError(list(data.keys()), list(variable_key_type_dict.keys()))

    if 'code' in data.keys() and type(data['code']) != variable_key_type_dict['code']:
        raise RequestDataTypeError('code', type(data['code']), variable_key_type_dict['code'])

    if 'tg_user_id' in data.keys() and type(data['tg_user_id']) != variable_key_type_dict['tg_user_id']:
        raise RequestDataTypeError('tg_user_id', type(data['tg_user_id']), variable_key_type_dict['tg_user_id'])


def student_get_validate(data: dict) -> None:
    variable_key_type_dict = {
        'code': str,
        'tg_user_id': int
    }

    if ('code' not in data.keys()) and ('tg_user_id' not in data.keys()):
        raise RequestDataKeysError(list(data.keys()), list(variable_key_type_dict.keys()))

    if 'code' in data.keys() and type(data['code']) != variable_key_type_dict['code']:
        raise RequestDataTypeError('code', type(data['code']), variable_key_type_dict['code'])

    if 'tg_user_id' in data.keys() and type(data['tg_user_id']) != variable_key_type_dict['tg_user_id']:
        raise RequestDataTypeError('tg_user_id', type(data['tg_user_id']), variable_key_type_dict['tg_user_id'])


def students_post_validate(data: dict) -> None:
    keys_type_dict = {
        "students": list,
    }

    key_type_validate(data, keys_type_dict)


def students_get_validate(data: dict) -> None:
    keys_type_dict = {
        "school_name": str,
    }

    key_type_validate(data, keys_type_dict)


def student_absent_post_validate(data: dict) -> None:
    key_type_dict = {
        'date': str,
        'reason': str,
    }
    variable_key_type_dict = {
        'code': str,
        'tg_user_id': int
    }

    for key, item in key_type_dict.items():
        if key not in data.keys():
            raise RequestDataMissedKeyError(key)
        if not isinstance(data[key], item):
            raise RequestDataTypeError(key, item, type(data[key]))

    if ('code' not in data.keys()) and ('tg_user_id' not in data.keys()):
        raise RequestDataKeysError(list(data.keys()), list(key_type_dict.keys()) + list(variable_key_type_dict.keys()))

    if 'code' in data.keys() and type(data['code']) != variable_key_type_dict['code']:
        raise RequestDataTypeError('code', type(data['code']), variable_key_type_dict['code'])

    if 'tg_user_id' in data.keys() and type(data['tg_user_id']) != variable_key_type_dict['tg_user_id']:
        raise RequestDataTypeError('tg_user_id', type(data['tg_user_id']), variable_key_type_dict['tg_user_id'])


def student_absent_get_validate(data: dict) -> None:
    key_type_dict = {
        'date': str,
        'reason': str,
    }
    variable_key_type_dict = {
        'code': str,
        'tg_user_id': int
    }

    if ('code' not in data.keys()) and ('tg_user_id' not in data.keys()):
        raise RequestDataKeysError(list(data.keys()), list(key_type_dict.keys()) + list(variable_key_type_dict.keys()))

    if 'code' in data.keys() and type(data['code']) != variable_key_type_dict['code']:
        raise RequestDataTypeError('code', type(data['code']), variable_key_type_dict['code'])

    if 'tg_user_id' in data.keys() and type(data['tg_user_id']) != variable_key_type_dict['tg_user_id']:
        raise RequestDataTypeError('tg_user_id', type(data['tg_user_id']), variable_key_type_dict['tg_user_id'])


def school_post_validate(data: dict) -> None:
    keys_type_dict = {
        "school_name": str,
    }

    key_type_validate(data, keys_type_dict)


def absents_get_validate(data: dict) -> None:
    keys_type_dict = {
        "school_name": str,
    }

    key_type_validate(data, keys_type_dict)