import sqlalchemy
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Teacher(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'teachers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)  # id
    tg_user_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True, nullable=True)  # teacher telegram id
    name = sqlalchemy.Column(sqlalchemy.String)  # teacher name
    surname = sqlalchemy.Column(sqlalchemy.String)  # teacher surname
    patronymic = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # teacher patronymic
    class_name = sqlalchemy.Column(sqlalchemy.String, unique=True)  # teacher class name
    code = sqlalchemy.Column(sqlalchemy.String, unique=True)  # teacher unique code
    school_name = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('schools.name'))  # teacher school name
    school = relationship('School', foreign_keys=[school_name])  # teacher school
    students = relationship("Student", back_populates='teacher', foreign_keys='Student.class_name')  # teacher student
