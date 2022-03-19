#!/usr/bin/env python3
# vim: fileencoding=utf-8
#
"""
This program concatenates text files by loading all of them at once, sorting
the rows alphabetically and writing them to stdout.

Usage: concat.py [file ...]

Example: concat.py a.txt b.txt > ab.txt
"""
import argparse

def load_file(filepath):
    """
    Load the textfile `filepath` into a list of rows.
    """
    with open(filepath, mode='r') as fobj:
        rows = list(fobj)

    return rows

def prepare_options():
    """
    Prepare the option parser.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("filename", nargs='+')

    return parser

def main():
    """
    Main program.
    """
    parser = prepare_options()
    args = parser.parse_args()

    rows = []
    for fpath in args.filename:
        _rows = load_file(fpath)
        rows.extend(_rows)

    for row in sorted(rows):
        print(row.rstrip())

if __name__ == '__main__':
    main()
