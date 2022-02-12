import sqlalchemy
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class School(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'schools'

    name = sqlalchemy.Column(sqlalchemy.String, unique=True, primary_key=True)  # school name
    link = sqlalchemy.Column(sqlalchemy.String)  # link to school google spreadsheets
    teachers = relationship("Teacher", back_populates='school', foreign_keys='Teacher.school_name')  # list of teachers
    students = relationship("Student", back_populates='user', foreign_keys='Student.school_name')  # list of students
