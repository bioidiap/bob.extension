from ..log import set_verbosity_level
from ..config import load, mod_to_context
import click
import logging

# This needs to be bob so that logger is configured for all bob packages.
logger = logging.getLogger('bob')
try:
  basestring
except NameError:
  basestring = str


def bool_option(name, short_name, desc, dflt=False, **kwargs):
  '''Generic provider for boolean options

  Parameters
  ----------
  name : str
      name of the option
  short_name : str
      short name for the option
  desc : str
      short description for the option
  dflt : bool or None
      Default value
  **kwargs
      All kwargs are passed to click.option.

  Returns
  -------
  callable
      A decorator to be used for adding this option.
  '''
  def custom_bool_option(func):
    def callback(ctx, param, value):
      ctx.meta[name.replace('-', '_')] = value
      return value
    return click.option(
        '-' + short_name, '--%s/--no-%s' % (name, name), default=dflt,
        help=desc,
        show_default=True, callback=callback, is_eager=True, **kwargs)(func)
  return custom_bool_option


def list_float_option(name, short_name, desc, nitems=None, dflt=None,
                      **kwargs):
  '''Get option to get a list of float f

  Parameters
  ----------
  name : str
      name of the option
  short_name : str
      short name for the option
  desc : str
      short description for the option
  nitems : obj:`int`, optional
      If given, the parsed list must contains this number of items.
  dflt : :any:`list`, optional
      List of default  values for axes.
  **kwargs
      All kwargs are passed to click.option.

  Returns
  -------
  callable
      A decorator to be used for adding this option.
  '''
  def custom_list_float_option(func):
    def callback(ctx, param, value):
      if value is None or not value.replace(' ', ''):
        value = None
      elif value is not None:
        tmp = value.split(',')
        if nitems is not None and len(tmp) != nitems:
          raise click.BadParameter(
              '%s Must provide %d axis limits' % (name, nitems)
          )
        try:
          value = [float(i) for i in tmp]
        except Exception:
          raise click.BadParameter('Inputs of %s be floats' % name)
      ctx.meta[name.replace('-', '_')] = value
      return value
    return click.option(
        '-' + short_name, '--' + name, default=dflt, show_default=True,
        help=desc + ' Provide just a space (\' \') to cancel default values.',
        callback=callback, **kwargs)(func)
  return custom_list_float_option


def open_file_mode_option(**kwargs):
  '''Get open mode file option

  Parameters
  ----------
  **kwargs
      All kwargs are passed to click.option.

  Returns
  -------
  callable
      A decorator to be used for adding this option.
  '''
  def custom_open_file_mode_option(func):
    def callback(ctx, param, value):
      if value not in ['w', 'a', 'w+', 'a+']:
        raise click.BadParameter('Incorrect open file mode')
      ctx.meta['open_mode'] = value
      return value
    return click.option(
        '-om', '--open-mode', default='w',
        help='File open mode',
        callback=callback, **kwargs)(func)
  return custom_open_file_mode_option


def verbosity_option(**kwargs):
  """Adds a -v/--verbose option to a click command.

  Parameters
  ----------
  **kwargs
      All kwargs are passed to click.option.

  Returns
  -------
  callable
      A decorator to be used for adding this option.
  """
  def custom_verbosity_option(f):
    def callback(ctx, param, value):
      ctx.meta['verbosity'] = value
      set_verbosity_level(logger, value)
      logger.debug("Logging of the `bob' logger was set to %d", value)
      return value
    return click.option(
        '-v', '--verbose', count=True,
        expose_value=False,
        help="Increase the verbosity level from 0 (only error messages) to 1 "
        "(warnings), 2 (log messages), 3 (debug information) by adding the "
        "--verbose option as often as desired (e.g. '-vvv' for debug).",
        callback=callback, **kwargs)(f)
  return custom_verbosity_option


class ConfigCommand(click.Command):
  """A click.Command that can take options both form command line options and
  configuration files. In order to use this class, you have to use the
  :any:`ResourceOption` class also.

  Attributes
  ----------
  config_argument_name : str
      The name of the config argument.
  entry_point_group : str
      The name of entry point that will be used to load the config files.
  """

  def __init__(self, name, context_settings=None, callback=None, params=None,
               help=None, epilog=None, short_help=None,
               options_metavar='[OPTIONS]',
               add_help_option=True, entry_point_group=None,
               config_argument_name='CONFIG', **kwargs):
    self.config_argument_name = config_argument_name
    self.entry_point_group = entry_point_group
    click.Command.__init__(
        self, name, context_settings=context_settings, callback=callback,
        params=params, help=help, epilog=epilog, short_help=short_help,
        options_metavar=options_metavar, add_help_option=add_help_option,
        **kwargs)
    # Add the config argument to the command
    click.argument(config_argument_name, nargs=-1)(self)

  def invoke(self, ctx):
    config_files = ctx.params[self.config_argument_name.lower()]
    # load and normalize context from config files
    config_context = load(
        config_files, entry_point_group=self.entry_point_group)
    config_context = mod_to_context(config_context)
    for param in self.params:
      if param.name not in ctx.params:
        continue
      value = ctx.params[param.name]
      if not hasattr(param, 'user_provided'):
        if value == param.default:
          param.user_provided = False
        else:
          param.user_provided = True
      if not param.user_provided and param.name in config_context:
        ctx.params[param.name] = param.full_process_value(
            ctx, config_context[param.name])
      # raise exceptions if the value is required.
      if hasattr(param, 'real_required'):
        param.required = param.real_required
        try:
          ctx.params[param.name] = param.full_process_value(
              ctx, ctx.params[param.name])
        finally:
          # make sure to set this back to False for future invocations
          param.required = False

    return super(ConfigCommand, self).invoke(ctx)


class ResourceOption(click.Option):
  """A click.Option that is aware if the user actually provided this option
  through command-line or it holds a default value. The option can also be a
  resource that will be automatically loaded.

  Attributes
  ----------
  entry_point_group : str or None
      If provided, the strings values to this option are assumed to be entry
      points from ``entry_point_group`` that need to be loaded.
  real_required : bool
      Holds the real value of ``required`` here. The ``required`` value is
      hidden from click since the option may be loaded later through the
      configuration files.
  user_provided : bool
      True if the user actually provided this option through command-line or
      using environment variables.
  """

  def __init__(self, param_decls=None, show_default=False, prompt=False,
               confirmation_prompt=False, hide_input=False, is_flag=None,
               flag_value=None, multiple=False, count=False,
               allow_from_autoenv=True, type=None, help=None,
               entry_point_group=None, required=False, **kwargs):
    self.entry_point_group = entry_point_group
    self.real_required = required
    kwargs['required'] = False
    click.Option.__init__(
        self, param_decls=param_decls, show_default=show_default,
        prompt=prompt, confirmation_prompt=confirmation_prompt,
        hide_input=hide_input, is_flag=is_flag, flag_value=flag_value,
        multiple=multiple, count=count, allow_from_autoenv=allow_from_autoenv,
        type=type, help=help, **kwargs)

  def consume_value(self, ctx, opts):
    value = opts.get(self.name)
    self.user_provided = True
    if value is None:
      value = ctx.lookup_default(self.name)
      self.user_provided = False
    if value is None:
      value = self.value_from_envvar(ctx)
      if value is not None:
        self.user_provided = True
    return value

  def full_process_value(self, ctx, value):
    value = super(ResourceOption,
                  self).full_process_value(ctx, value)

    if self.entry_point_group is not None:
      keyword = self.entry_point_group.split('.')[-1]
      while isinstance(value, basestring):
        value = load([value], entry_point_group=self.entry_point_group)
        value = getattr(value, keyword)

    return value

class AliasedGroup(click.Group):
  ''' Class that handles prefix aliasing for commands

  Basically just implements get_command that is used by click to choose the
  comamnd based on the name.

  Example
  -------
  To enable prefix aliasing of commands for a given group,
  just set ``cls=AliasedGroup`` parameter in click.group decorator.
  '''
  def get_command(self, ctx, cmd_name):
    rv = click.Group.get_command(self, ctx, cmd_name)
    if rv is not None:
      return rv
    matches = [x for x in self.list_commands(ctx)
               if x.startswith(cmd_name)]
    if not matches:
      return None
    elif len(matches) == 1:
      return click.Group.get_command(self, ctx, matches[0])
    ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))
