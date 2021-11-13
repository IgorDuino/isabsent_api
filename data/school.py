import sqlalchemy
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


# Класс школы
class School(SqlAlchemyBase, SerializerMixin):
    # Название таблицы
    __tablename__ = 'schools'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True)
    teachers = relationship("Teacher", back_populates='school', foreign_keys='Teacher.school_name')
    students = relationship("Student", back_populates='school', foreign_keys='Student.school_name')