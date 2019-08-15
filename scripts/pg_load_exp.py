#!/usr/bin/env python3
"""
Author : Ken Youens-Clark <kyclark@email.arizona.edu>
Date   : 2019-08-08
Purpose: Biosphere2 drought load experiment
"""

import argparse
import csv
import json
import os
import pandas as pd
import logging
import psycopg2
from typing import Iterable, List, TextIO
from result import Ok, Err
from configparser import ConfigParser


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='B2 load experiment',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-c',
                        '--config',
                        help='DB config file',
                        metavar='FILE',
                        type=argparse.FileType('r'),
                        default='db.conf')

    parser.add_argument('-f',
                        '--file',
                        help='Experiment data file (CSV)',
                        metavar='FILE',
                        type=argparse.FileType('r'),
                        required=True)

    # parser.add_argument('-T',
    #                     '--type',
    #                     help='Experiment type',
    #                     metavar='str',
    #                     type=str,
    #                     choices=['VOCs'],
    #                     default='VOCs')

    # parser.add_argument('-o',
    #                     '--outfile',
    #                     help='Output file',
    #                     metavar='FILE',
    #                     type=str,
    #                     default='samples.json')

    parser.add_argument('-d',
                        '--debug',
                        help='Debug to .log',
                        action='store_true')

    # parser.add_argument('-p',
    #                     '--pretty',
    #                     help='Pretty JSON output',
    #                     action='store_true')

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.CRITICAL,
        filename='.log',
        filemode='w')

    return args


# --------------------------------------------------
def main():
    """Make a jazz noise here"""

    args = get_args()

    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config(args.config, 'db')
        print(params)

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

       # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

    # exp_file = args.file
    # #exp_type = args.type

    # samples_df = pd.read_csv(exp_file)
    # logging.debug('Got %s samples from %s', len(samples_df), exp_file.name)

    # columns = samples_df.columns
    # logging.debug('Columns = %s', ', '.join(columns))

    # check_columns(columns, args.type, args.topology)
    # logging.debug('Samples file OK')

    # col_meta = get_column_metadata(columns, args.vocabulary)
    # logging.debug('Got column meta')

    # num_exported = export_samples(samples_df, col_meta, args.outfile, args.pretty)
    # logging.debug('Exported %s samples to "%s"', num_exported, args.outfile)

    # print(f'Done, see output "{args.outfile}".')


# --------------------------------------------------
def check_columns(columns, exp_type, topo_file):
    """
    Check samples with topology

    Topology file looks like this:

    Term            : Experiment_type
    Types           : VOCs
    Subtypes        :
    required_fields : sample_ID
    """

    topo = pd.read_csv(topo_file)
    types = topo[topo['Types'] == exp_type]
    assert not types.empty

    req_flds = types['required_fields'].tolist()
    logging.debug('req_flds = %s', ', '.join(req_flds))

    missing = list(filter(lambda fld: fld not in columns, req_flds))
    if missing:
        raise Exception('samples missing = %s', ', '.join(missing))

    return True


# --------------------------------------------------
def get_column_metadata(columns, vocab_file):
    """
    Get column metadata

    Vocab file looks like this:

    Term           : sample_ID
    Displayed_term : sample ID
    Definition     : Unique identifier for the sample.
    Section_object : Specimen_description
    Units          :
    Type           : string
    Aliases        :
    """

    vocab = pd.read_csv(vocab_file)
    col_meta = {}
    missing = []
    for col in columns:
        terms = vocab[vocab['Term'] == col]
        if len(terms) == 1:
            term = terms.iloc[0]
            col_meta[col] = {
                'section': term['Section_object'].lower(),
                'type': term['Type'].lower()
            }
        else:
            missing.append(col)

    if missing:
        msg = 'Columns "{}" not in vocabulary file'.format(', '.join(missing))
        raise Exception(msg)

    return col_meta


# --------------------------------------------------
def export_samples(samples_df, col_meta, out_file, pretty):
    """Export samples to out_file"""

    samples = []
    for index, row in samples_df.iterrows():
        sample, result, files = {}, {}, {}
        for fld in samples_df.columns:
            meta = col_meta.get(fld)
            section = meta['section']
            dtype = meta['type']
            val = row[fld]

            if dtype == 'date-time':
                val = {'$date': val}

            if meta:
                if meta['section'] == 'result':
                    result[fld] = val
                elif meta['section'] == 'file':
                    files[fld] = val
                else:
                    sample[fld] = val

        sample['Result'] = result
        sample['files'] = files
        samples.append(sample)

    out_fh = open(out_file, 'wt')
    out_fh.write(json.dumps(samples, indent=4 if pretty else 0))

    return len(samples)

# --------------------------------------------------
def config(fh, section='db'):
    """Read config file"""

    parser = ConfigParser()
    parser.read_string(fh.read())

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

# --------------------------------------------------
if __name__ == '__main__':
    main()
