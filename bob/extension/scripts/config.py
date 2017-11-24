"""The manager for bob's main configuration.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from .. import rc
from ..rc_config import _saverc, _dumprc, _get_rc_path
from argparse import RawDescriptionHelpFormatter
import logging
import sys


def setup_parser(parser):
    from . import __doc__ as docs
    # creates a top-level parser for this database
    top_level = parser.add_parser('config',
                                  formatter_class=RawDescriptionHelpFormatter,
                                  help=docs)

    subparsers = top_level.add_subparsers(title="subcommands")

    # add commands
    show_command(subparsers)
    get_command(subparsers)
    set_command(subparsers)

    return subparsers


def show(arguments=None):
    """Shows the content of bob's global configuration file.
    """
    print("The configuration is located at {}".format(_get_rc_path()))
    print("It's content are:")
    _dumprc(rc, sys.stdout)


def show_command(subparsers):
    parser = subparsers.add_parser('show', help=show.__doc__)
    parser.set_defaults(func=show)
    return parser


def get(arguments):
    """Gets the specified configuration from bob's global configuration file.

    Parameters
    ----------
    arguments : argparse.Namespace
        A set of arguments passed by the command-line parser


    Returns
    -------
    int
        A POSIX compliant return value of ``0`` if the key exists, or ``1``
        otherwise.
    """
    value = rc[arguments.key]
    if value is None:
        return 1
    print(value)
    return 0


def get_command(subparsers):
    parser = subparsers.add_parser('get', help=get.__doc__)
    parser.add_argument("key", help="The requested key.")
    parser.set_defaults(func=get)
    return parser


def set(arguments):
    """Sets the specified configuration to the provided value in bob's global
    configuration file.

    Parameters
    ----------
    arguments : argparse.Namespace
        A set of arguments passed by the command-line parser


    Returns
    -------
    int
        A POSIX compliant return value of ``0`` if the operation is successful,
        or ``1`` otherwise.
    """
    try:
        rc[arguments.key] = arguments.value
        _saverc(rc)
    except Exception:
        logging.warn("Could not configure the rc file", exc_info=True)
        return 1
    return 0


def set_command(subparsers):
    parser = subparsers.add_parser('set', help=set.__doc__)
    parser.add_argument("key", help="The key.")
    parser.add_argument("value", help="The value.")
    parser.set_defaults(func=set)
    return parser
