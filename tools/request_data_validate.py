from error_book import *


def teacher_post_validate(data: dict) -> None:
    keys_type_dict = {
        'name': str,
        'surname': str,
        'patronymic': str,
        'class_name': str,
        'school_name': str
    }

    for key, item in keys_type_dict.items():
        if key not in data.keys():
            raise RequestDataMissedKeyError(key)
        if not isinstance(data[key], item):
            raise RequestDataTypeError(key, item, type(data[key]))

    if len(data.keys()) != len(keys_type_dict.keys()):
        raise RequestDataKeysError(list(data.keys()), list(keys_type_dict.keys()))


# def teacher_patch_validate(data: dict) -> None:
#     keys_type_dict = {
#         'name': str,
#         'surname': str,
#         'patronymic': str,
#         'class_name': str,
#         'school_name': str
#     }
#
#     if 'code' not in data.keys() and 'tg_user_id' not in data.keys():
#         raise RequestDataMissedKeyError('code')
#
#     for key, item in keys_type_dict.items():
#         if key in data.keys() and not isinstance(data[key], item):
#             raise RequestDataTypeError(key, item, type(data[key]))
#
#     if len(data) == 1:
#         raise RequestDataKeysError(['id'], list(keys_type_dict.keys()))


def student_post_validate(data: dict) -> None:
    keys_type_dict = {
        'name': str,
        'surname': str,
        'patronymic': str,
        'class_name': str,
        'school_name': str
    }

    for key, item in keys_type_dict.items():
        if key not in data.keys():
            raise RequestDataMissedKeyError(key)
        if not isinstance(data[key], item):
            raise RequestDataTypeError(key, item, type(data[key]))

    if len(data.keys()) != len(keys_type_dict.keys()):
        raise RequestDataKeysError(list(data.keys()), list(keys_type_dict.keys()))