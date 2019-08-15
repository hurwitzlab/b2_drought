#!/usr/bin/env python3

import sqlalchemy
import b2.db
from b2.model import Test
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --------------------------------------------------
def main():
    """start here"""

    session = b2.db.session()
    new = b2.db.get_or_create(session, Test, val='baz')
    session.commit()

    for rec in session.query(Test):
        print(rec.val)

main()
