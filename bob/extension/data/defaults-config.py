#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

'''Advanced configuration for my jet pack'''

import os
# Objects whose name start with an underscore are not returned by ``load()``
_model = os.path.expanduser('~/.jet-pack-model.hdf5')
del os

# Package defaults
defaults['bob.db.atnt'] = {
    'directory': '/directory/to/root/of/atnt-database',
    'extension': '.ppm',
    }
