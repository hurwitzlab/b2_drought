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
from typing import Iterable, List, TextIO
from result import Ok, Err


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='B2 load experiment',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-f',
                        '--file',
                        help='Experiment data file (CSV)',
                        metavar='FILE',
                        type=argparse.FileType('r'),
                        required=True)

    parser.add_argument('-v',
                        '--vocabulary',
                        help='Vocabulary file (CSV)',
                        metavar='FILE',
                        type=argparse.FileType('r'),
                        required=True)

    parser.add_argument('-t',
                        '--topology',
                        help='Topology file (CSV)',
                        metavar='FILE',
                        type=argparse.FileType('r'),
                        required=True)

    parser.add_argument('-T',
                        '--type',
                        help='Experiment type',
                        metavar='str',
                        type=str,
                        choices=['VOCs'],
                        default='VOCs')

    parser.add_argument('-o',
                        '--outfile',
                        help='Output file',
                        metavar='FILE',
                        type=str,
                        default='samples.json')

    parser.add_argument('-d',
                        '--debug',
                        help='Debug to .log',
                        action='store_true')

    parser.add_argument('-p',
                        '--pretty',
                        help='Pretty JSON output',
                        action='store_true')

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
    exp_file = args.file
    #exp_type = args.type

    samples_df = pd.read_csv(exp_file)
    logging.debug('Got %s samples from %s', len(samples_df), exp_file.name)

    columns = samples_df.columns
    logging.debug('Columns = %s', ', '.join(columns))

    check_samples(columns, args.type, args.topology)
    logging.debug('Samples file OK')

    col_meta = get_column_metadata(samples_df, args.vocabulary)
    logging.debug('Got column meta')

    samples = []
    for index, row in samples_df.iterrows():
        sample, result, files = {}, {}, {}
        for fld in columns:
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

    logging.debug('Encoding %s samples to %s', len(samples), args.outfile)
    out_fh = open(args.outfile, 'wt')
    out_fh.write(json.dumps(samples, indent=4 if args.pretty else 0))
    print(f'Done, see output "{args.outfile}".')


# --------------------------------------------------
def check_samples(columns, exp_type, topo_file):
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
        logging.critical('samples missing = %s', ', '.join(missing))
        return False

    return True


# --------------------------------------------------
def get_column_metadata(samples_df, vocab_file):
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
    for col in samples_df.columns:
        terms = vocab[vocab['Term'] == col]
        if len(terms) == 1:
            term = terms.iloc[0]
            col_meta[col] = {
                'section': term['Section_object'].lower(),
                'type': term['Type'].lower()
            }
        else:
            logging.warning(f'Column "{col}" not in vocabulary file')

    return col_meta


# --------------------------------------------------
if __name__ == '__main__':
    main()
