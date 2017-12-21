"""This is the main entry to bob's scripts.
"""
import pkg_resources
import click
from click_plugins import with_plugins
from ..log import setup, set_verbosity_level
logger = setup('bob')


@with_plugins(pkg_resources.iter_entry_points('bob.cli'))
@click.group()
@click.option(
    '-v',
    '--verbose',
    count=True,
    help="Increase the verbosity level from 0 (only error messages) to 1 "
    "(warnings), 2 (log messages), 3 (debug information) by adding the "
    "--verbose option as often as desired (e.g. '-vvv' for debug).")
@click.option(
    '--log',
    type=click.File('wb'),
    help='Redirects the prints of the scripts to FILENAME.')
def main(verbose, log):
  """The main command line interface for bob.
  Look below for available commands."""
  set_verbosity_level(logger, verbose)
  logger.debug("Logging of the `bob' logger was set to %d", verbose)
  ctx = click.get_current_context()
  ctx.meta['verbosity'] = verbose
  ctx.meta['log_file'] = log
