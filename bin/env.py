#!/usr/bin/env python
# vim: fileencoding=utf-8 fileformat=unix
# $Id: env.py 2214 2020-02-24 13:11:50Z wissa $
"""
Print environment variables in readable form. The supplied value is
interpreted as a regular expression. All environment variables matching
the pattern will be printed.

Case insensitive.
@author: %(username)s
"""
import argparse
import os
import re

DEFAULT_EXPR = 'LOCAL_PATH'

def find_ev(param):
    """
    Find environment variable containing param.
    """
    all_ev = sorted(os.environ.keys())
    pat = re.compile(param, flags=re.IGNORECASE)

    e_vars = [(ev, os.getenv(ev)) for ev in all_ev if pat.search(ev)]

    return e_vars


def main():
    u"""
    Traitement des arguments.
    Impression du résultat.
    """

    parser = prepare_options()
    args = parser.parse_args()

    psep = args.separator or os.pathsep
    regexpr = args.regular_expression

    env = find_ev(regexpr)
    if not env:
        print("%s: No value" % regexpr)
    for env_var, value in env:
        # Find separator between paths
        sep = re.search(psep, value)
        if sep:
            paths = value.split(sep.group(0))
            print("%s =" % env_var)
            for path in paths:
                print(" %s" % path)
        else:
            print("%s = %s" % (env_var, value))


def prepare_options():
    """
    Prepare the option parser and return it.
    """

    usage = ("%(prog)s\n\nPrint environment variables. If separated "
             "by a path separator, print on \nseparate lines. Case "
             "insensitive. The argument is a regular expression. "
             "All variables matching the pattern will be printed.")

    parser = argparse.ArgumentParser(usage=usage)

    parser.add_argument('regular_expression',
                        help=(u"Expression régulière qui identifie les "
                              u"valeurs des variables à afficher. Par "
                              u"défaut, cette expression est \"%s\".") %\
                                DEFAULT_EXPR,
                        nargs='?',
                        default=DEFAULT_EXPR)


    parser.add_argument('--separator', '-s',
                        help=('Character that separates variables (ex: `:` '
                              'for path in Linux). Platform dependent value '
                              'provided for paths on Mac OS and Windows'),
                        default=None)

    return parser

main()
