"""This is the main entry to bob's scripts.
"""
import pkg_resources
import click
from click_plugins import with_plugins
from .click_helper import AliasedGroup
from ..log import setup
logger = setup('bob')


@with_plugins(pkg_resources.iter_entry_points('bob.cli'))
@click.group(cls=AliasedGroup,
             context_settings=dict(help_option_names=['-?', '-h', '--help']))
def main():
  """The main command line interface for bob. Look below for available
  commands."""
  pass
