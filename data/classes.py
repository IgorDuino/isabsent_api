# import sqlalchemy
# from sqlalchemy.orm import relationship
# from .db_session import SqlAlchemyBase
# from sqlalchemy_serializer import SerializerMixin
#
#
# class Class(SqlAlchemyBase, SerializerMixin):
#     __tablename__ = 'classes'
#
#     id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)  # id
#     title = sqlalchemy.Column(sqlalchemy.String)  # teacher name
#     teacher_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('schools.name'))  # teacher school name
#     school = relationship('School', foreign_keys=[school_name])  # teacher school
#     students = relationship("Student", back_populates='teacher', foreign_keys='Student.class_name')  # teacher student
