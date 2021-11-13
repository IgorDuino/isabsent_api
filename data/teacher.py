import sqlalchemy
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


# Класс учителя
class Teacher(SqlAlchemyBase, SerializerMixin):
    # Название таблицы
    __tablename__ = 'teachers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    class_name = sqlalchemy.Column(sqlalchemy.String)

    def __setitem__(self, key, value):
        if key == 'id':
            self.id = value
        elif key == 'name':
            self.name = value
        elif key == 'class_name':
            self.class_name = value