import click
import time
import pkg_resources
from click.testing import CliRunner
from bob.extension.scripts.click_helper import (
    verbosity_option, bool_option, list_float_option,
    ConfigCommand, ResourceOption, AliasedGroup)


def test_verbosity_option():

    for VERBOSITY, OPTIONS in zip([0, 1, 2, 3],
                                  [[], ['-v'], ['-vv'], ['-vvv']]):
        @click.command()
        @verbosity_option()
        def cli(verbose):
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

    @cli.command(name='test-aaa')
    def test_aaa():
        click.echo("AAA")

    runner = CliRunner()
    result = runner.invoke(cli, ['te'], catch_exceptions=False)
    assert result.exit_code != 0, (result.exit_code, result.output)

    result = runner.invoke(cli, ['test'], catch_exceptions=False)
    assert result.exit_code == 0, (result.exit_code, result.output)
    assert 'OK' in result.output, (result.exit_code, result.output)

    result = runner.invoke(cli, ['test-a'], catch_exceptions=False)
    assert result.exit_code == 0, (result.exit_code, result.output)
    assert 'AAA' in result.output, (result.exit_code, result.output)


def _assert_config_dump(ref, ref_date):
    today = time.strftime("%d/%m/%Y")
    # uncomment below to re-write tests
    # open(ref, 'wt').write(open('TEST_CONF').read())
    with open('TEST_CONF', 'r') as f, open(ref, 'r') as f2:
        text = f.read()
        ref_text = f2.read().replace(ref_date, today)
        assert text == ref_text, '\n'.join([text, ref_text])


def test_config_dump():
    @click.group(cls=AliasedGroup)
    def cli():
        pass

    @cli.command(cls=ConfigCommand, epilog='Examples!')
    @click.option('-t', '--test', required=True, default="/my/path/test.txt",
                  help="Path leading to test blablabla", cls=ResourceOption)
    @verbosity_option()
    def test(config, test, **kwargs):
        """Test command"""
        pass
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli, ['test', '-H', 'TEST_CONF'], catch_exceptions=False)
        ref = pkg_resources.resource_filename('bob.extension',
                                              'data/test_dump_config.py')
        assert result.exit_code == 0, (result.exit_code, result.output)
        _assert_config_dump(ref, '08/07/2018')


def test_config_dump2():
    @click.group(cls=AliasedGroup)
    def cli():
        pass

    @cli.command(cls=ConfigCommand, entry_point_group='bob.extension.test_dump_config')
    @click.option('--database', '-d', required=True, cls=ResourceOption,
                  entry_point_group='bob.extension.test_dump_config', help="bla bla bla")
    @click.option('--annotator', '-a', required=True, cls=ResourceOption,
                  entry_point_group='bob.extension.test_dump_config', help="bli bli bli")
    @click.option('--output-dir', '-o', required=True, cls=ResourceOption,
                  help="blo blo blo")
    @click.option('--force', '-f', is_flag=True, cls=ResourceOption,
                  help="lalalalalala")
    @click.option('--array', type=click.INT, default=1, cls=ResourceOption,
                  help="lililili")
    @click.option('--database-directories-file', cls=ResourceOption,
                  default='~/databases.txt', help="lklklklk")
    @verbosity_option(cls=ResourceOption)
    def test(**kwargs):
        """Blablabla bli blo

        Parameters
        ----------
        xxx : :any:`list`
            blabla blablo
        yyy : callable
            bli bla blo bla bla bla

        [CONFIG]...           BLA BLA BLA BLA
        """
        pass

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli, ['test', '-H', 'TEST_CONF'], catch_exceptions=False)
        ref = pkg_resources.resource_filename('bob.extension',
                                              'data/test_dump_config2.py')
        assert result.exit_code == 0, (result.exit_code, result.output)
        _assert_config_dump(ref, '08/07/2018')
