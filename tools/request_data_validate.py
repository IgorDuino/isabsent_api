def teacher_post_validate(data: dict) -> None:
    keys_type_dict = {
        'id': int,
        'class_name': str,
        'teacher_name': str
    }

    for key, item in keys_type_dict.items():
        if not isinstance(data[key], item):
            raise ValueError(f'Не верный тип name must be{str} get{type(data["name"])}')

    if data.keys() not in keys_type_dict.keys():
        raise KeyError('Набор ключей в запросе не соответствует шаблону валидации')