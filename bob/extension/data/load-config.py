# relative paths are considered w.r.t. location of the caller
# the following will load the file ``advanced-config.py`` which
# is located alongside this file
defaults = load('defaults-config.py')['defaults']

# overrides a particular default or sets it for the first time
update(defaults, {'bob.db.atnt': {'extension': '.hdf5'}})
