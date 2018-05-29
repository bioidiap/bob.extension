import click
from click.testing import CliRunner
from bob.extension.scripts.click_helper import (
    verbosity_option, bool_option, list_float_option,
    open_file_mode_option, ConfigCommand, ResourceOption, AliasedGroup)


def test_verbosity_option():

    for VERBOSITY, OPTIONS in zip([0, 1, 2, 3],
                                  [[], ['-v'], ['-vv'], ['-vvv']]):
        @click.command()
        @verbosity_option()
        def cli():
            ctx = click.get_current_context()
            verbose = ctx.meta['verbosity']
            assert verbose == VERBOSITY, verbose

        runner = CliRunner()
        result = runner.invoke(cli, OPTIONS, catch_exceptions=False)
        assert result.exit_code == 0, (result.exit_code, result.output)

def test_bool_option():

    @click.command()
    @bool_option('i-am-test', 'T', 'test test test', True)
    def cli(i_am_test):
        ctx = click.get_current_context()
        is_test = ctx.meta['i_am_test']
        assert i_am_test == is_test
        assert is_test

    @click.command()
    @bool_option('i-am-test', 'T', 'test test test', False)
    def cli2(i_am_test):
        ctx = click.get_current_context()
        is_test = ctx.meta['i_am_test']
        assert i_am_test == is_test
        assert not is_test

    runner = CliRunner()
    result = runner.invoke(cli)
    assert result.exit_code == 0, (result.exit_code, result.output)

    result = runner.invoke(cli2)
    assert result.exit_code == 0, (result.exit_code, result.output)

def test_list_float_option():

    @click.command()
    @list_float_option('test-list', 'T', 'Test list')
    def cli(test_list):
        ctx = click.get_current_context()
        test = ctx.meta['test_list']
        assert test == test_list
        assert test == [1, 2, 3]

    runner = CliRunner()
    result = runner.invoke(cli, ['-T', '1,2,3'])
    assert result.exit_code == 0, (result.exit_code, result.output)

def test_list_float_option_empty():

    @click.command()
    @list_float_option('test-list', 'T', 'Test list')
    def cli(test_list):
        ctx = click.get_current_context()
        test = ctx.meta['test_list']
        assert test is None

    runner = CliRunner()
    result = runner.invoke(cli, ['-T', ' '])
    assert result.exit_code == 0, (result.exit_code, result.output)

def test_commands_with_config_1():
    # random test
    @click.command(
        cls=ConfigCommand, entry_point_group='bob.extension.test_config_load')
    def cli(**kwargs):
        pass

    runner = CliRunner()
    result = runner.invoke(cli, ['basic_config'])
    assert result.exit_code == 0, (result.exit_code, result.output)


def test_commands_with_config_2():
    # test option with valid default value
    @click.command(
        cls=ConfigCommand, entry_point_group='bob.extension.test_config_load')
    @click.option(
        '-a', cls=ResourceOption, default=3)
    def cli(a, **kwargs):
        click.echo('{}'.format(a))

    runner = CliRunner()

    result = runner.invoke(cli, [])
    assert result.exit_code == 0, (result.exit_code, result.output)
    assert result.output.strip() == '3', result.output

    result = runner.invoke(cli, ['basic_config'])
    assert result.exit_code == 0, (result.exit_code, result.output)
    assert result.output.strip() == '1', result.output

    result = runner.invoke(cli, ['-a', 2])
    assert result.exit_code == 0, (result.exit_code, result.output)
    assert result.output.strip() == '2', result.output

    result = runner.invoke(cli, ['-a', 3, 'basic_config'])
    assert result.exit_code == 0, (result.exit_code, result.output)
    assert result.output.strip() == '3', result.output

    result = runner.invoke(cli, ['basic_config', '-a', 3])
    assert result.exit_code == 0, (result.exit_code, result.output)
    assert result.output.strip() == '3', result.output


def test_commands_with_config_3():
    # test required options
    @click.command(
        cls=ConfigCommand, entry_point_group='bob.extension.test_config_load')
    @click.option(
        '-a', cls=ResourceOption, required=True)
    def cli(a, **kwargs):
        click.echo('{}'.format(a))

    runner = CliRunner()

    result = runner.invoke(cli, [])
    assert result.exit_code == 2, (result.exit_code, result.output)

    result = runner.invoke(cli, ['basic_config'])
    assert result.exit_code == 0, (result.exit_code, result.output)
    assert result.output.strip() == '1', result.output

    result = runner.invoke(cli, ['-a', 2])
    assert result.exit_code == 0, (result.exit_code, result.output)
    assert result.output.strip() == '2', result.output

    result = runner.invoke(cli, ['-a', 3, 'basic_config'])
    assert result.exit_code == 0, (result.exit_code, result.output)
    assert result.output.strip() == '3', result.output

    result = runner.invoke(cli, ['basic_config', '-a', 3])
    assert result.exit_code == 0, (result.exit_code, result.output)
    assert result.output.strip() == '3', result.output

def test_prefix_aliasing():
    @click.group(cls=AliasedGroup)
    def cli():
        pass

    @cli.command()
    def test():
        click.echo("OK")

    @cli.command()
    def test_aaa():
        click.echo("AAA")


    runner = CliRunner()
    result = runner.invoke(cli, ['te'], catch_exceptions=False)
    assert result.exit_code != 0, (result.exit_code, result.output)

    result = runner.invoke(cli, ['test'], catch_exceptions=False)
    assert result.exit_code == 0, (result.exit_code, result.output)
    assert 'OK' in result.output, (result.exit_code, result.output)

    result = runner.invoke(cli, ['test_a'], catch_exceptions=False)
    assert result.exit_code == 0, (result.exit_code, result.output)
    assert 'AAA' in result.output, (result.exit_code, result.output)
