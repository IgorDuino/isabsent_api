from error_book import *


def key_type_validate(data: dict, keys_type_dict: dict) -> None:
    for key, item in keys_type_dict.items():
        if key not in data.keys():
            raise RequestDataMissedKeyError(key)
        if not isinstance(data[key], item):
            raise RequestDataTypeError(key, item, type(data[key]))

    if len(data.keys()) != len(keys_type_dict.keys()):
        raise RequestDataKeysError((list(data.keys()), list(keys_type_dict.keys())))


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