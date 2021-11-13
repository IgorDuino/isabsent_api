import sqlalchemy
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin



# Класс учителя
class Teacher(SqlAlchemyBase, SerializerMixin):
    # Название таблицы
    __tablename__ = 'teachers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    tg_user_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    surname = sqlalchemy.Column(sqlalchemy.String)
    patronymic = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    class_name = sqlalchemy.Column(sqlalchemy.String)
    code = sqlalchemy.Column(sqlalchemy.Integer, default=0, unique=True)
    school_name = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('schools.name'))
    school = relationship('School', foreign_keys=[school_name])

    def __setitem__(self, key, value):
        if key == 'name':
            self.name = value
        elif key == 'class_name':
            self.class_name = value