"""The manager for bob's main configuration.
"""
from .. import rc
from ..rc_config import _saverc, _rc_to_str, _get_rc_path
import logging
import click

logger = logging.getLogger(__name__)


@click.group()
def config():
    """The manager for bob's global configuration."""
    # Load the config file again. This may be needed since the environment
    # variable might change the config path during the tests. Otherwise, this
    # should not be important.
    logger.debug('Reloading the global configuration file.')
    from ..rc_config import _loadrc
    rc.clear()
    rc.update(_loadrc())


@config.command()
def show():
    """Shows the configuration.

    Displays the content of bob's global configuration file.
    """
    log_file = click.get_current_context().meta['log_file']
    click.echo("Displaying `{}':".format(_get_rc_path()), log_file)
    click.echo(_rc_to_str(rc), log_file)


@config.command()
@click.argument('key')
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
    log_file = click.get_current_context().meta['log_file']
    value = rc[key]
    if value is None:
        raise click.ClickException(
            "The requested key `{}' does not exist".format(key))
    click.echo(value, log_file)


@config.command()
@click.argument('key')
@click.argument('value')
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
