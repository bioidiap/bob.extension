#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Functionality to implement python-based config file parsing and loading.
"""

import logging
import pkgutil
import types

from collections import defaultdict
from os.path import isfile

import pkg_resources

logger = logging.getLogger(__name__)

LOADED_CONFIGS = []


def _load_context(path, mod):
    """Loads the Python file as module, returns a resolved context

    This function is implemented in a way that is both Python 2 and Python 3
    compatible. It does not directly load the python file, but reads its contents
    in memory before Python-compiling it. It leaves no traces on the file system.

    Parameters
    ----------
    path : str
        The full path of the Python file to load the module contents
        from
    mod : module
        A preloaded module to use as context for the next module
        loading. You can create a new module using :py:mod:`types` as in ``m =
        types.ModuleType('name'); m.__dict__.update(ctxt)`` where ``ctxt`` is a
        python dictionary with string -> object values representing the contents
        of the module to be created.

    Returns
    -------
    mod : :any:`module`
        A python module with the fully resolved context
    """

    # executes the module code on the context of previously imported modules
    with open(path, "rb") as f:
        exec(compile(f.read(), path, "exec"), mod.__dict__)

    return mod


def _get_module_filename(module_name):
    """Resolves a module name to an actual Python file.

    Parameters
    ----------
    module_name : str
        The name of the module

    Returns
    -------
    str
        The Python files that corresponds to the module name.
    """
    loader = pkgutil.get_loader(module_name)
    if loader is None:
        return ""
    try:
        return loader.path
    except AttributeError:
        return loader.filename


def _object_name(path, common_name):
    path = path.rsplit(":", 1)
    name = path[1] if len(path) > 1 else common_name
    path = path[0]
    return path, name


def _resolve_entry_point_or_modules(paths, entry_point_group, common_name=None):
    """Resolves a mixture of paths, entry point names, and module names to just
    paths. For example paths can be:
    ``paths = ['/tmp/config.py', 'config1', 'bob.extension.config2']``.

    Parameters
    ----------
    paths : [str]
        An iterable strings that either point to actual files, are entry point
        names, or are module names.
    entry_point_group : str
        The entry point group name to search in entry points.
    common_name : None or str
        It will be used as a default name for object names. See the
        attribute_name parameter from :any:`load`.

    Raises
    ------
    ValueError
        If one of the paths cannot be resolved to an actual path to a file.

    Returns
    -------
    paths : [str]
        The resolved paths pointing to existing files.
    module_names : [str]
        The valid python module names to bind each of the files to
    object_names : [str]
        The name of objects that are supposed to be picked from paths.
    """

    entries = {
        e.name: e for e in pkg_resources.iter_entry_points(entry_point_group)
    }

    files = []
    module_names = []
    object_names = []

    for i, path in enumerate(paths):

        old_path = path
        module_name = (
            "user_config"  # fixed module name for files with full paths
        )
        path, object_name = _object_name(path, common_name)

        # if it already points to a file
        if isfile(path):
            pass

        # If it is an entry point name, collect path and module name
        elif path in entries:
            entry = entries[path]
            module_name = entry.module_name
            object_name = entry.attrs[0] if entry.attrs else common_name
            path = _get_module_filename(module_name)
            if not isfile(path):
                raise ValueError(
                    "The specified entry point: `{}' pointing to module: `{}' and "
                    "resolved to: `{}' does not point to an existing "
                    "file.".format(old_path, module_name, path)
                )

        # If it is not a path nor an entry point name, it is a module name then?
        else:
            # if we have gotten here so far then path is the module_name.
            module_name = path
            path = _get_module_filename(path)
            if not isfile(path):
                raise ValueError(
                    "The specified path: `{}' resolved to: `{}' is not a file, not a "
                    "entry point name of `{}', nor a module name".format(
                        old_path, path, entry_point_group or ""
                    )
                )

        files.append(path)
        module_names.append(module_name)
        object_names.append(object_name)

    return files, module_names, object_names


def load(paths, context=None, entry_point_group=None, attribute_name=None):
    """Loads a set of configuration files, in sequence

    This method will load one or more configuration files. Every time a
    configuration file is loaded, the context (variables) loaded from the
    previous file is made available, so the new configuration file can override
    or modify this context.

    Parameters
    ----------
    paths : [str]
        A list or iterable containing paths (relative or absolute) of
        configuration files that need to be loaded in sequence. Each
        configuration file is loaded by creating/modifying the context generated
        after each file readout.
    context : :py:class:`dict`, optional
        If provided, start the readout of the first configuration file with the
        given context. Otherwise, create a new internal context.
    entry_point_group : :py:class:`str`, optional
        If provided, it will treat non-existing file paths as entry point names
        under the ``entry_point_group`` name.
    attribute_name : None or str
        If provided, will look for the attribute_name variable inside the loaded
        files. Paths ending with `some_path:variable_name` can override the
        attribute_name. The entry_point_group must provided as well
        attribute_name is not None.

    Returns
    -------
    mod : :any:`module` or object
        A module representing the resolved context, after loading the provided
        modules and resolving all variables. If attribute_name is given, the
        object with the attribute_name name (or the name provided by user) is
        returned instead of the module.

    Raises
    ------
    ImportError
        If attribute_name is given but the object does not exist in the paths.
    ValueError
        If attribute_name is given but entry_point_group is not given.

    """
    if attribute_name and not entry_point_group:
        raise ValueError(
            "entry_point_group must be provided when using the "
            "attribute_name parameter."
        )

    # resolve entry points to paths
    if entry_point_group is not None:
        paths, names, object_names = _resolve_entry_point_or_modules(
            paths, entry_point_group, attribute_name
        )
    else:
        names = len(paths) * ["user_config"]

    ctxt = types.ModuleType("initial_context")
    if context is not None:
        ctxt.__dict__.update(context)
    # Small gambiarra (https://www.urbandictionary.com/define.php?term=Gambiarra)
    # to avoid the garbage collector to collect some already imported modules.
    LOADED_CONFIGS.append(ctxt)

    # if no paths are provided, return context
    if not paths:
        return ctxt

    for k, n in zip(paths, names):
        logger.debug("Loading configuration file `%s'...", k)
        mod = types.ModuleType(n)
        # remove the keys that might break the loading of the next config file.
        ctxt.__dict__.pop("__name__", None)
        ctxt.__dict__.pop("__package__", None)
        # do not propogate __ variables
        context = {
            k: v for k, v in ctxt.__dict__.items() if not k.startswith("__")
        }
        mod.__dict__.update(context)
        LOADED_CONFIGS.append(mod)
        ctxt = _load_context(k, mod)

    if not attribute_name:
        return mod

    # We pick the last object_name here. Normally users should provide just one
    # path when enabling the attribute_name parameter.
    attribute_name = object_names[-1]
    if not hasattr(mod, attribute_name):
        raise ImportError(
            "The desired variable '%s' does not exist in any of "
            "your configuration files: %s" % (attribute_name, ", ".join(paths))
        )

    return getattr(mod, attribute_name)


def mod_to_context(mod):
    """Converts the loaded module of :any:`load` to a dictionary context.
    This function removes all the variables that start and end with ``__``.

    Parameters
    ----------
    mod : object
        What is returned by :any:`load`

    Returns
    -------
    dict
        The context that was in ``mod``.
    """
    return {
        k: v
        for k, v in mod.__dict__.items()
        if not (k.startswith("__") and k.endswith("__"))
    }


def resource_keys(
    entry_point_group,
    exclude_packages=[],
    strip=["dummy"],
    with_project_names=False,
):
    """Reads and returns all resources that are registered with the given
    entry_point_group. Entry points from the given ``exclude_packages`` are
    ignored.

    Parameters
    ----------
    entry_point_group : str
        The entry point group name.
    exclude_packages : :any:`list`, optional
        List of packages to exclude when finding resources.
    strip : :any:`list`, optional
        Entrypoint names that start with any value in ``strip`` will be ignored.
    with_project_names : :any:`bool`, optional
        If True, will return a list of tuples with the project name and the entry point name.

    Returns
    -------
    :any:`list`
        List of found entry point names. If ``with_project_names`` is True, will return
        a list of tuples with the project name and the entry point name.
    """
    if with_project_names:
        ret_list = defaultdict(list)
    else:
        ret_list = []

    for entry_point in pkg_resources.iter_entry_points(entry_point_group):
        if not (
            entry_point.dist.project_name not in exclude_packages
            and not entry_point.name.startswith(tuple(strip))
        ):
            continue
        if with_project_names:
            ret_list[str(entry_point.dist.project_name)].append(
                entry_point.name
            )
        else:
            ret_list.append(entry_point.name)

    if with_project_names:
        # sort each list inside the dict
        ret_list = {k: sorted(v) for k, v in ret_list.items()}
    else:
        ret_list = sorted(ret_list)

    return ret_list
