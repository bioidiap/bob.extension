'''Tests for the global bob's configuration functionality'''

from .rc_config import _loadrc, ENVNAME
from .scripts import main_cli
import os
import pkg_resources
import tempfile
path = pkg_resources.resource_filename('bob.extension', 'data')


def test_rc_env():

    os.environ[ENVNAME] = os.path.join(path, 'defaults-config')
    c = _loadrc()  # should load from environment variable
    REFERENCE = {
        "bob.db.atnt.directory": "/home/bob/databases/atnt",
        "bob.db.mobio.directory": "/home/bob/databases/mobio"
    }

    assert c == REFERENCE
    assert c['random'] is None


def test_bob_config():
    os.environ[ENVNAME] = os.path.join(path, 'defaults-config')
    main_cli(['config', 'get', 'bob.db.atnt.directory'])
    with tempfile.NamedTemporaryFile('wt') as f:
        os.environ[ENVNAME] = f.name
        main_cli(['config', 'set', 'bob.db.atnt.directory',
                  '/home/bob/databases/atnt'])
        main_cli(['config', 'show'])
