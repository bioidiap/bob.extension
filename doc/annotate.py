"""A script to help annotate databases.
"""
# Avoid importing packages here! Importing packages here will slowdown your command
# line's --help option and its auto-complete feature in terminal (if enabled). Instead,
# put your imports inside the function.
import logging
import click
from bob.extension.scripts.click_helper import (
    verbosity_option, ConfigCommand, ResourceOption, log_parameters)

logger = logging.getLogger(__name__)


@click.command(entry_point_group='bob.bio.config', cls=ConfigCommand,
               epilog='''\b
Examples:

  $ bob bio annotate -vvv -d <database> -a <annotator> -o /tmp/annotations
  $ jman submit --array 64 -- bob bio annotate ... --array 64
''')
@click.option('--database', '-d', required=True, cls=ResourceOption,
              entry_point_group='bob.bio.database',
              help='''The database that you want to annotate.''')
@click.option('--annotator', '-a', required=True, cls=ResourceOption,
              entry_point_group='bob.bio.annotator',
              help='A callable that takes the database and a sample (biofile) '
              'of the database and returns the annotations in a dictionary.')
@click.option('--output-dir', '-o', required=True, cls=ResourceOption,
              help='The directory to save the annotations.')
@click.option('--force', '-f', is_flag=True, cls=ResourceOption,
              help='Whether to overwrite existing annotations.')
@click.option('--array', type=click.INT, default=1, cls=ResourceOption,
              help='Use this option alongside gridtk to submit this script as '
              'an array job.')
@verbosity_option(cls=ResourceOption)
def annotate(database, annotator, output_dir, force, array, **kwargs):
    """Annotates a database.

    The annotations are written in text file (json) format which can be read
    back using :any:`bob.db.base.read_annotation_file` (annotation_type='json')
    """
    log_parameters(logger)

    # Add imports needed for your code here:
    import numpy as np

    np.zeros(10)
