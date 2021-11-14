import sqlalchemy
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


# Класс отсутствия
class Absent(SqlAlchemyBase, SerializerMixin):
    # Название таблицы
    __tablename__ = 'absents'

    date = sqlalchemy.Column(sqlalchemy.Date)
    reason = sqlalchemy.Column(sqlalchemy.String)
    student_code = sqlalchemy.Column(sqlalchemy.String, unique=True, primary_key=True)
    student = relationship('School', foreign_keys=[student_code])