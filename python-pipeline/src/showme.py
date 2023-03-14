import logging
import json
import pandas as pd
from urllib import request
from os import path, mkdir
from showcase import runForConfig


def main():
    logging.basicConfig(format="%(funcName)s: %(message)s", level=logging.INFO)
    output_dir = path.join('.', 'german_credit_showcase')
    sensitive_microdata_path = path.join(output_dir, 'german_credit_data.tsv')

    if not path.exists(output_dir):
        mkdir(output_dir)

    if not path.exists(sensitive_microdata_path):
        attributes = []
        codes = {}
        logging.info('Retrieving data documentation...')
        codes_file = request.urlopen(
            'https://archive.ics.uci.edu/ml/machine-learning-databases/statlog/german/german.doc').readlines()
        logging.info('Retrieved')
        state = 'skip'
        attribute = ''
        code = ''
        value = ''
        for line in [x.decode('UTF-8').strip() for x in codes_file]:
            if line == '':
                state = 'skip'
            elif state == 'skip':
                if str.startswith(line, 'Att'):
                    state = 'attribute'
            elif state == 'attribute':
                attribute = line.strip()
                attributes.append(attribute)
                codes[attribute] = {}
                state = 'values'
            elif state == 'values':
                split = line.index(':') if ':' in line else -1
                if split != -1:
                    code = line[:split].strip()
                    value = line[split+1:].strip().replace(':', '-')
                    codes[attribute][code] = value
                else:
                    codes[attribute][code] += ' ' + line.replace(':', '-')
        attributes.append('Credit rating')
        codes['Credit rating'] = {'1': 'Good', '2': 'Bad'}

        logging.info('Retrieving data file...')
        df = pd.read_csv('https://archive.ics.uci.edu/ml/machine-learning-databases/statlog/german/german.data',
                         sep=' ', index_col=False, header=None, names=attributes)

        logging.info('Retrieved')
        logging.info('Processing dataset...')
        values, labels = binValuesAndLabels(df['Duration in month'].max(), 12)
        df['Duration in month'] = pd.cut(
            df['Duration in month'], bins=values, labels=labels)
        values, labels = binValuesAndLabels(df['Credit amount'].max(), 2500)
        df['Credit amount'] = pd.cut(
            df['Credit amount'], bins=values, labels=labels)
        values, labels = binValuesAndLabels(df['Age in years'].max(), 20)
        df['Age in years'] = pd.cut(
            df['Age in years'], bins=values, labels=labels)

        df = df.astype(str).replace(to_replace=r'^nan$', value='', regex=True)

        for att in attributes:
            df[att] = df[att].replace(codes[att])

        df = df.drop(
            ['foreign worker', 'Property', 'Telephone', 'Other debtors / guarantors',
             'Number of people being liable to provide maintenance for', 'Other installment plans',
             'Savings account/bonds', 'Present employment since', 'Status of existing checking account'],
            axis=1)

        df.to_csv(sensitive_microdata_path, sep='\t', index=False)
        logging.info('Processed')

    config = {
        'parallel_jobs': 1,
        'cache_max_size': 100000,
        'multi_value_columns': {},
        'use_columns': [],
        'record_limit': -1,
        'reporting_length': 5,
        'reporting_resolution': 2,
        'synthesis_mode': 'row_seeded',
        'sensitive_zeros': [],
        'output_dir': output_dir,
        'sensitive_microdata_path': sensitive_microdata_path,
        'sensitive_microdata_delimiter': '\t',
        'report_title': 'German Credit Data Showcase',
        'prefix': 'example',
    }

    config['aggregate'] = True
    config['generate'] = True
    config['navigate'] = True
    config['evaluate'] = True

    runForConfig(config)


def binValuesAndLabels(max_value, bin_size):
    values = [0]
    labels = []
    upper = bin_size
    while upper < max_value:
        values.append(upper)
        labels.append(f'{upper-bin_size}-{upper}')
        upper += bin_size
    return values, labels


if __name__ == '__main__':
    main()
