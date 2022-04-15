import sqlalchemy
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Absent(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'absents'

    id = sqlalchemy.Column(sqlalchemy.Integer, unique=True, primary_key=True, autoincrement=True)   # id
    date = sqlalchemy.Column(sqlalchemy.Date)   # date when student absent
    reason = sqlalchemy.Column(sqlalchemy.String)   # absent reason
    file = sqlalchemy.Column(sqlalchemy.LargeBinary, nullable=True)    # file with proof
    student_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('students.id'))  # absent student id
    student = relationship('Student', foreign_keys=[student_id])    # student that absent
