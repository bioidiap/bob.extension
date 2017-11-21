#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

'''Advanced configuration for my jet pack'''

import os as _os
# Objects whose name start with an underscore are not returned by ``load()``
_model = _os.path.expanduser('~/.jet-pack-model.hdf5')

# Package defaults
defaults['bob.db.atnt'] = {
    'directory': '/directory/to/root/of/atnt-database',
    'extension': '.ppm',
}
