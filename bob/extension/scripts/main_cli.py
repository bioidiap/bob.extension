"""This is the main entry to bob's scripts.
As of now it just supports `bob config`.
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import argparse

epilog = """  For a list of available commands:
  >>> %(prog)s --help

  For a list of actions on each command:
  >>> %(prog)s <command> --help
"""


def create_parser(**kwargs):
    """Creates a parser for the central manager taking into consideration the
    options for every module that can provide those."""

    parser = argparse.ArgumentParser(**kwargs)
    subparsers = parser.add_subparsers(title='commands')

    return parser, subparsers


def main(argv=None):
    from argparse import RawDescriptionHelpFormatter
    parser, subparsers = create_parser(
        description=__doc__, epilog=epilog,
        formatter_class=RawDescriptionHelpFormatter)

    # for now there is only the config command so we'll just add it here.
    # Normally, this would be added in a better way in future. Maybe something
    # similar to bob_dbmanage.py
    from .config import setup_parser
    setup_parser(subparsers)

    args = parser.parse_args(args=argv)
    if hasattr(args, 'func'):
        return args.func(args)
    else:
        return parser.parse_args(args=['--help'])


if __name__ == '__main__':
    main()
