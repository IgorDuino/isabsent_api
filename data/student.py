import sqlalchemy
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


# Класс студента
class Student(SqlAlchemyBase, SerializerMixin):
    # Название таблицы
    __tablename__ = 'students'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    tg_user_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    surname = sqlalchemy.Column(sqlalchemy.String)
    patronymic = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    class_name = sqlalchemy.Column(sqlalchemy.String)
    code = sqlalchemy.Column(sqlalchemy.String, default=0, unique=True)
    school_name = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('schools.name'))
    school = relationship('School', foreign_keys=[school_name])
    # absents = relationship("Absent", back_populates='student', foreign_keys='Student.student_code')