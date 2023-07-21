from sqlalchemy import Column, Integer, String, func, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql.sqltypes import Date, DateTime

Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    __table_args__ = (
        UniqueConstraint('email', 'user_id', name='unique_contact_user'),
    )
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column(String(13), nullable=True)
    birth_date = Column(Date, default=func.now())
    created_at = Column('created_at', DateTime, default=func.now())
    description = Column(String(250), nullable=True)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user = relationship('User', backref="contacts")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column('crated_at', DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
