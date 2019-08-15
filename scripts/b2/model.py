# coding: utf-8
from sqlalchemy import Column, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Cv(Base):
    __tablename__ = 'cv'

    cv_id = Column(Integer, primary_key=True, server_default=text("nextval('cv_cv_id_seq'::regclass)"))
    term = Column(String(50), unique=True)
    display_name = Column(String(50))
    definition = Column(String(50))
    section = Column(String(50))
    units = Column(String(50))
    dtype = Column(String(50))
    aliases = Column(String(50))


class Test(Base):
    __tablename__ = 'test'

    id = Column(Integer, primary_key=True, server_default=text("nextval('test_id_seq'::regclass)"))
    val = Column(String(10))
