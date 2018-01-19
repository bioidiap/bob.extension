"""This is the main entry to bob's scripts.
"""
import pkg_resources
import click
from click_plugins import with_plugins
from ..log import setup, set_verbosity_level
logger = setup('bob')


def verbosity_option(f):
  def callback(ctx, param, value):
    ctx.meta['verbosity'] = value
    set_verbosity_level(logger, value)
    logger.debug("Logging of the `bob' logger was set to %d", value)
    return value
  return click.option(
      '-v', '--verbose', count=True,
      expose_value=False,
      help="Increase the verbosity level from 0 (only error messages) to 1 "
      "(warnings), 2 (log messages), 3 (debug information) by adding the "
      "--verbose option as often as desired (e.g. '-vvv' for debug).",
      callback=callback)(f)


@with_plugins(pkg_resources.iter_entry_points('bob.cli'))
@click.group()
def main():
  """The main command line interface for bob. Look below for available
  commands."""
  pass
