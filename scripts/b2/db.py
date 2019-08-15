"""B2 db"""

import os
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from configparser import ConfigParser

# --------------------------------------------------
def dbh(**args):
    """Connect to db"""

    return psycopg2.connect(args)

# --------------------------------------------------
def session(dsn='postgres:///b2', echo=False):
    """SQLAlchemy session"""

    engine = create_engine(dsn, echo=echo)
    Session = sessionmaker(bind=engine)
    return Session()

# --------------------------------------------------
def get_or_create(session, model, **kwargs):
    """
    Get or create a model instance while preserving integrity.
    """
    try:
        return session.query(model).filter_by(**kwargs).one(), False
    except Exception as e:
        try:
            with session.begin_nested():
                instance = model(**kwargs)
                session.add(instance)
                return instance, True
        except Exception as e:
            return session.query(model).filter_by(**kwargs).one(), False
