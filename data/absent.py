import sqlalchemy
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


# Класс отсутствия
class Absent(SqlAlchemyBase, SerializerMixin):
    # Название таблицы
    __tablename__ = 'absents'

    id = sqlalchemy.Column(sqlalchemy.Integer, unique=True, primary_key=True, autoincrement=True)
    date = sqlalchemy.Column(sqlalchemy.Date)
    reason = sqlalchemy.Column(sqlalchemy.String)
    file = sqlalchemy.Column(sqlalchemy.BINARY, nullable=True)
    student_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('students.id'))
    student = relationship('Student', foreign_keys=[student_id])