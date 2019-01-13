import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'picture': self.picture,
            'email': self.email}


class University(Base):
    __tablename__ = 'university'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id}


class College(Base):
    __tablename__ = 'college'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    department = Column(String(250))
    university_id = Column(Integer, ForeignKey('university.id'))
    university = relationship(University)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'department': self.department,
            'id': self.id}


engine = create_engine('sqlite:///universities.db')
Base.metadata.create_all(engine)
