#!/usr/bin/env python3

import csv
import b2.db
from b2.model import Cv


# --------------------------------------------------
def main():
    """start here"""

    session = b2.db.session()
    file = '/Users/kyclark/work/b2/b2_drought/vocabulary/experiment_controlled_vocabulary.csv'
    with open(file) as fh:
        for i, row in enumerate(csv.DictReader(fh), start=1):
            print(f"{i:3d}: {row['Term']}")
            new = dict(term=row['Term'],
                       display_name=row['Displayed_term'],
                       definition=row['Definition'],
                       section=row['Section_object'],
                       units=row['Units'],
                       dtype=row['Type'],
                       aliases=row['Aliases'])
            res, inserted = b2.db.get_or_create(session, Cv, **new)

    session.commit()

# --------------------------------------------------
if __name__ == '__main__':
    main()
