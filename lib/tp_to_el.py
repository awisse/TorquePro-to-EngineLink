#!/usr/bin/env python3
# vim: fileencoding=utf-8
#
# This program converts TorquePro exdended PID files from the site
# (https://github.com/JejuSoul/OBD-PIDs-for-HKMC-EVs)
# into extended PID files for EngineLink
# (http://outdoor-apps.com/enginelink.html)
"""
Import a TorquePro PID file and transform it into an EngineLink PID file.

The TorquePro filename must be <name>.csv. The resuluting filename will be
 <name>-EL.csv.
"""
import argparse
import csv
import re
import sys
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
SHIFT_RE = r'\(([A-Z]{1,2})<(8|16|24)\)'
SIGNED_RE = r'Signed(?P<signed>\([A-Za-z]{1,2}\))'

def int16_conv(matchobj):
    """
    `matchobj`: re.match expression.
    Returns a formula that computes the 16 bit integer from the
    two bytes in the expression.
    """
    formula = '({}*256+{})'.format(*matchobj.groups())
    return formula

def int32_conv(matchobj):
    """
    `matchobj`: re.match expression
    Returns a formula that computes the 32 bit integer from the
    four bytes in the expression.
    """
    formula = '((({}*256+{})*256+{})*256+{})'.format(*matchobj.groups())
    return formula

def shift_conv(matchobj):
    """
    Transform '(a<b)' into 'a * 2**b'.
    """
    shift = 1 << int(matchobj.group(2))
    formula = '{}*{}'.format(matchobj.group(1), shift)
    return formula

def torquepro_variables(tp_file):
    """
    Extract all variable names from the `tp_file` (A TorquePro file) for
    substitution in the parsing pass. A dictonary is returned with the
    TorquePro variable name as key and the TorquePro description as
    the EngineLink variable name.
    """
    variables = {}
    reader = csv.DictReader(tp_file, fieldnames=TP_FIELDS, delimiter=',')

    variables = {row[VAR].lower() : row[DESC] for row in reader}

    # Rewind the file
    tp_file.seek(0)

    return variables

def torquepro_to_enginelink_formula(tp_formula, variables):
    """
    Replace variable names in the `tp_formula` with names accepted
    by EngineLink, that is '[DESC]'.
    """
    # Make a copy
    el_formula = str(tp_formula)

    # Replace `Signed` function
    el_formula = re.sub(SIGNED_RE, 'SIGNED\g<signed>', el_formula)

    # Replace `Bit` function.
    el_formula = re.sub(BIT_RE, '{\g<bit>}', el_formula)

    # Replace `Int16` function
    el_formula = re.sub(INT16_RE, int16_conv, el_formula, flags=re.IGNORECASE)

    # Replace `Int32` function
    el_formula = re.sub(INT32_RE, int32_conv, el_formula, flags=re.IGNORECASE)

    # Replace `<` (bit shift)
    el_formula = re.sub(SHIFT_RE, shift_conv, el_formula, flags=re.IGNORECASE)

    return el_formula

def torquepro_to_enginelink_row(row, variables):
    """
    Transform a TorquePro row into an EngineLink row.
    `row`: A dictionary of Va
    """
    # Copy unmodified values. Order is preserved. ECU is copied as last
    # element.
    engine_link = {k : row[k] for k in COPY_FIELDS}

    formula = row[FORMULA]

    # Replace variable names
    var_replacements = 0
    for var in variables:
        tp_var = f'val{{{var}}}'
        # Use re.subn in order to recover number of replacements
        formula, replaced = re.subn(tp_var, f'[{variables[var]}]',
                                    formula, flags=re.IGNORECASE)
        var_replacements += replaced

    # If there is a tp_formula with variables, EngineLink doesn't want a PID
    # and no values from the scanner are used.
    if var_replacements > 0:
        engine_link[PID] = ''
        engine_link[FORMULA] = formula
    else:
        # Get the EngineLink formula from the TorquePro formula
        engine_link[FORMULA] =\
            torquepro_to_enginelink_formula(formula, variables)
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

def dir_argument(arg):
    """
    Check whether argument is a directory.
    """
    dir_arg = Path(arg)
    if not dir_arg.is_dir():
        raise argparse.ArgumentError('--target-dir must be a directory')

    return dir_arg

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
                        type=dir_argument,
                        default=Path('.'))

    parser.add_argument('--to-stdout', '-O',
                        help=('Write the resulting file to stdout and *not* '
                              'to a .csv file.'),
                        action='store_true',
                        default=False)
    return parser

def process_file(tp_file, el_file):
    """
    `tp_file`: Readable file object.
    `el_file`: Writable file object.
    Read every line from the `tp_file` and write the EngineLink version
    to the `el_file`.
    """
    # Storage for variables
    variables = torquepro_variables(tp_file)

    # CSV file reader and writer
    reader = csv.DictReader(tp_file, fieldnames=TP_FIELDS, delimiter=',')
    writer = csv.DictWriter(el_file, EL_FIELDS, delimiter=',')
    writer.writerow(dict(zip(EL_FIELDS, EL_FIELDS)))

    for tp_row in reader:
        el_row = torquepro_to_enginelink_row(tp_row, variables)
        writer.writerow(el_row)

def main():
    """
    Exécuter le code.
    """
    # Option parsing
    parser = prepare_options()
    args = parser.parse_args()

    # Input Filename
    tp_path = args.tp_file

    # Opening TorquePro file for reading
    tp_file = open(tp_path, mode='r', errors='replace', newline='')

    # Opening EngineLink file for writing
    if args.to_stdout:
        el_file = sys.stdout
    else:
        el_name = f'{tp_path.stem}-EL.csv'
        el_path = args.target_dir.joinpath(el_name)
        try:
            el_file = open(el_path, mode='w', newline='')
        except OSError:
            sys.stderr.write(f'The file "{el_name}" cannot be written\n')
            sys.exit(1)

    # Convert the lines
    process_file(tp_file, el_file)

    tp_file.close()
    if not args.to_stdout:
        el_file.close()
