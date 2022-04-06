import sqlalchemy
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Student(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'students'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)  # id
    tg_user_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)  # student telegram id
    name = sqlalchemy.Column(sqlalchemy.String)  # student name
    surname = sqlalchemy.Column(sqlalchemy.String)  # student surname
    patronymic = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # student patronymic
    class_name = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('teachers.class_name'))  # class name
    teacher = relationship('Teacher', foreign_keys=[class_name])  # student teacher
    code = sqlalchemy.Column(sqlalchemy.String, unique=True)  # student unique code
    school_name = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('schools.name'))  # student school name
    school = relationship('School', foreign_keys=[school_name])  # student school
    absents = relationship("Absent", back_populates='student', foreign_keys='Absent.student_id')  # student absent list
