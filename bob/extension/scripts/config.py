"""The manager for bob's main configuration.
"""
import logging

import click

from .. import rc
from ..rc_config import _get_rc_path, _rc_to_str, _saverc
from .click_helper import AliasedGroup, verbosity_option

# Use the normal logging module. Verbosity and format of logging will be set by
# adding the verbosity_option form bob.extension.scripts.click_helper
logger = logging.getLogger(__name__)


@click.group(cls=AliasedGroup)
@verbosity_option()
def config(**kwargs):
    """The manager for bob's global configuration."""
    # Load the config file again. This may be needed since the environment
    # variable might change the config path during the tests. Otherwise, this
    # should not be important.
    logger.debug("Reloading the global configuration file.")
    from ..rc_config import _loadrc

    rc.clear()
    rc.update(_loadrc())


@config.command()
def show():
    """Shows the configuration.

    Displays the content of bob's global configuration file.
    """
    # always use click.echo instead of print
    click.echo("Displaying `{}':".format(_get_rc_path()))
    click.echo(_rc_to_str(rc))


@config.command()
@click.argument("key")
def get(key):
    """Prints a key.

    Retrieves the value of the requested key and displays it.

    \b
    Arguments
    ---------
    key : str
        The key to return its value from the configuration.

    \b
    Fails
    -----
    * If the key is not found.
    """
    value = rc[key]
    if value is None:
        # Exit the command line with ClickException in case of errors.
        raise click.ClickException(
            "The requested key `{}' does not exist".format(key)
        )
    click.echo(value)


@config.command()
@click.argument("key")
@click.argument("value")
def set(key, value):
    """Sets the value for a key.

    Sets the value of the specified configuration key in bob's global
    configuration file.

    \b
    Arguments
    ---------
    key : str
        The key to set the value for.
    value : str
        The value of the key.

    \b
    Fails
    -----
    * If something goes wrong.
    """
    try:
        rc[key] = value
        _saverc(rc)
    except Exception:
        logger.error("Could not configure the rc file", exc_info=True)
        raise click.ClickException("Failed to change the configuration.")


@config.command()
@click.argument("substr")
@click.option(
    "-c",
    "--contain",
    is_flag=True,
    default=False,
    type=click.BOOL,
    show_default=True,
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    default=False,
    type=click.BOOL,
    show_default=True,
)
def unset(substr, contain=False, force=False):
    """Clear all variables starting (containing) with substring.

    Clear all the variables that starts with the provided substring.
    Each key/value pair for which the key starts with substring will be
    removed from bob's global configuration file.

    \b
    Arguments
    ---------
    substring : str
        The starting substring of one or several key(s)

    \b
    Parameters
    ----------
    contain : bool
        If set, check also for keys containing substring
    force : bool
        If set, unset values without confirmation
    """
    found = False
    to_delete = []
    for key in list(rc.keys()):
        if key.startswith(substr):
            found = True
            to_delete.append(key)
        if contain:
            if substr in key:
                to_delete.append(key)
                found = True

    if not found:
        if not contain:
            logger.error(
                "The key starting with '{}' was not found in the rc file".format(
                    substr
                )
            )
        else:
            logger.error(
                "The key containing '{}' was not found in the rc file".format(
                    substr
                )
            )

        raise click.ClickException("Failed to change the configuration.")

    if force:
        for key in to_delete:
            del rc[key]
    else:
        click.echo("Registered for deletion:")
        for key in to_delete:
            click.echo('- "{}" : "{}"'.format(key, rc[key]))
        delete = click.confirm("Are you sure you want to delete all this ?")
        if delete:
            for key in to_delete:
                del rc[key]

    _saverc(rc)
