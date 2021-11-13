import sqlalchemy
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


# Класс студента
class Student(SqlAlchemyBase, SerializerMixin):
    # Название таблицы
    __tablename__ = 'students'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, nullable=True, autoincrement=True)