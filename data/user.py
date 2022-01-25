import sqlalchemy
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, unique=True, primary_key=True)
    login = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    enabled = sqlalchemy.Column(sqlalchemy.Boolean)