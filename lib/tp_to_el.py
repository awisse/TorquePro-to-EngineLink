#!/usr/bin/env python3
# vim: fileencoding=utf-8
#
"""
Import a TorquePro PID file and transform it into an EngineLink PID file.

The TorquePro filename must be <name>.csv. The resuluting filename will be
 <name>-EL.csv.
"""
import argparse
import csv
import re
from pathlib import Path

# Field Names
VAR = 'Variable'
DESC = 'Description'
PID = 'ModePID'
FORMULA = 'Formula'
MIN = 'Min'
MAX = 'Max'
ECU = 'Header'
UNIT = 'Units'

TP_FIELDS = [VAR, DESC, PID, FORMULA, MIN, MAX, UNIT, ECU]
EL_FIELDS = [PID, DESC, MIN, MAX, UNIT, FORMULA, ECU]
COPY_FIELDS = [PID, DESC, MIN, MAX, UNIT, ECU]

BIT_RE = r'Bit\((?P<bit>[A-Za-z]{1,2}:[0-7])\)'
INT16_RE = r'Int16\(([A-Z]{1,2}):([A-Z]{1,2})\)'
INT32_RE = r'Int32\(([A-Z]{1,2}):([A-Z]{1,2}):([A-Z]{1,2}):([A-Z]{1,2})\)'
SIGNED_RE = r'Signed(?P<signed>\([A-Za-z]{1,2}\))'

def int16_conv(matchobj):
    """
    `matchobj`: re.match expression.
    Returns a formula that computes the 16 bit integer from the
    two bytes in expr.
    """
    formula = '({}*256+{})'.format(*matchobj.groups())
    return formula

def int32_conv(matchobj):
    """
    `matchobj`: re.match expression
    Returns a formula that computes the 32 bit integer from the
    two bytes in expr.
    """
    formula = '((({}*256+{})*256+{})*256+{})'.format(*matchobj.groups())
    return formula

def torquepro_to_enginelink_formula(tp_formula, variables):
    """
    Replace variable names in the `tp_formula` with names accepted
    by EngineLink, that is '[DESC]'.
    """
    # Make a copy
    el_formula = str(tp_formula)

    # Replace variable names
    for var in variables:
        tp_var = f'val{{{var}}}'
        el_formula = el_formula.replace(tp_var, f'[{variables[var]}]')

    # Replace `Signed` function
    el_formula = re.sub(SIGNED_RE, 'SIGNED\g<signed>', el_formula)

    # Replace `Bit` function.
    el_formula = re.sub(BIT_RE, '{\g<bit>}', el_formula)

    # Replace `Int16` function
    el_formula = re.sub(INT16_RE, int16_conv, el_formula, flags=re.IGNORECASE)

    # Replace `Int32` function
    el_formula = re.sub(INT32_RE, int32_conv, el_formula, flags=re.IGNORECASE)

    return el_formula

def torquepro_to_enginelink_row(row, variables):
    """
    Transform a TorquePro row into an EngineLink row.
    `row`: A dictionary of Va
    """
    # Copy unmodified values. Order is preserved. ECU is copied as last
    # element.
    engine_link = {k : row[k] for k in COPY_FIELDS}

    # Get the variable name and define EngineLink variable
    variables[row[VAR]] = row[DESC]

    # Get the EngineLink formula from the TorquePro formula
    engine_link[FORMULA] = torquepro_to_enginelink_formula(row[FORMULA],
                                                           variables)
    return engine_link

def filetype_argument(arg):
    """
    Check whether the file defined by `arg` exists.
    """
    fpath = Path(arg).resolve()
    if not fpath.exists():
        raise argparse.ArgumentError(f'File "{arg}" doesn\'t exist.')

    if not fpath.suffix == '.csv':
        raise argparse.ArgumentError('Filename must end in .csv')

    return fpath

def prepare_options():
    """
    Prepare the option parser.
    """
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('tp_file',
                        help='The name/path of the TorquePro file',
                        type=filetype_argument)

    parser.add_argument('--target-dir', '-d',
                        help=('The directory where the transformed file will '
                              'be saved. Default: "."'),
                        default=Path('.'))

    return parser

def main():
    """
    Exécuter le code.
    """
    # Option parsing
    parser = prepare_options()
    args = parser.parse_args()

    # Storage for variables
    variables = {}

    # Output Filename
    tp_path = args.tp_file

    el_name = f'{Path(args.tp_file).stem}-EL.csv'
    el_path = Path(args.target_dir).joinpath(el_name)

    # Opening TorquePro file for reading
    with open(tp_path, mode='r', errors='replace',
              newline='') as tp_file:
        reader = csv.DictReader(tp_file, fieldnames=TP_FIELDS, delimiter=',')
        # Opening EngineLink file for writing
        with open(el_path, mode='w', newline='') as el_file:
            writer = csv.DictWriter(el_file, EL_FIELDS, delimiter=',')
            writer.writerow(dict(zip(EL_FIELDS, EL_FIELDS)))
            for tp_row in reader:
                el_row = torquepro_to_enginelink_row(tp_row, variables)
                writer.writerow(el_row)
