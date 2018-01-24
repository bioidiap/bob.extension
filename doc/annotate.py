"""A script to help annotate databases.
"""
import logging
import click
from bob.extension.scripts.click_helper import (
    verbosity_option, Command, Option)

logger = logging.getLogger(__name__)


@click.command(entry_point_group='bob.bio.config', cls=Command)
@click.option('--database', '-d', required=True, cls=Option,
              entry_point_group='bob.bio.database')
@click.option('--annotator', '-a', required=True, cls=Option,
              entry_point_group='bob.bio.annotator')
@click.option('--output-dir', '-o', required=True, cls=Option)
@click.option('--force', '-f', is_flag=True, cls=Option)
@verbosity_option(cls=Option)
def annotate(database, annotator, output_dir, force, **kwargs):
    """Annotates a database.
    The annotations are written in text file (json) format which can be read
    back using :any:`bob.db.base.read_annotation_file` (annotation_type='json')

    \b
    Parameters
    ----------
    database : :any:`bob.bio.database`
        The database that you want to annotate. Can be a ``bob.bio.database``
        entry point or a path to a Python file which contains a variable
        named `database`.
    annotator : callable
        A function that takes the database and a sample (biofile) of the
        database and returns the annotations in a dictionary. Can be a
        ``bob.bio.annotator`` entry point or a path to a Python file which
        contains a variable named `annotator`.
    output_dir : str
        The directory to save the annotations.
    force : bool, optional
        Wether to overwrite existing annotations.
    verbose : int, optional
        Increases verbosity (see help for --verbose).

    \b
    [CONFIG]...            Configuration files. It is possible to pass one or
                           several Python files (or names of ``bob.bio.config``
                           entry points) which contain the parameters listed
                           above as Python variables. The options through the
                           command-line (see below) will override the values of
                           configuration files.
    """
    print('database', database)
    print('annotator', annotator)
    print('force', force)
    print('output_dir', output_dir)
    print('kwargs', kwargs)
