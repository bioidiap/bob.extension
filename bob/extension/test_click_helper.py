import time

import click
import pkg_resources

from click.testing import CliRunner

from bob.extension.scripts.click_helper import (
    AliasedGroup,
    ConfigCommand,
    ResourceOption,
    assert_click_runner_result,
    bool_option,
    list_float_option,
    verbosity_option,
)


def test_verbosity_option():

    for VERBOSITY, OPTIONS in zip(
        [0, 1, 2, 3], [[], ["-v"], ["-vv"], ["-vvv"]]
    ):

        @click.command()
        @verbosity_option()
        def cli(verbose):
            ctx = click.get_current_context()
            verbose = ctx.meta["verbosity"]
            assert verbose == VERBOSITY, verbose

        runner = CliRunner()
        result = runner.invoke(cli, OPTIONS, catch_exceptions=False)
        assert_click_runner_result(result)


def test_bool_option():
    @click.command()
    @bool_option("i-am-test", "T", "test test test", True)
    def cli(i_am_test):
        ctx = click.get_current_context()
        is_test = ctx.meta["i_am_test"]
        assert i_am_test == is_test
        assert is_test

    @click.command()
    @bool_option("i-am-test", "T", "test test test", False)
    def cli2(i_am_test):
        ctx = click.get_current_context()
        is_test = ctx.meta["i_am_test"]
        assert i_am_test == is_test
        assert not is_test

    runner = CliRunner()
    result = runner.invoke(cli)
    assert_click_runner_result(result)

    result = runner.invoke(cli2)
    assert_click_runner_result(result)


def test_list_float_option():
    @click.command()
    @list_float_option("test-list", "T", "Test list")
    def cli(test_list):
        ctx = click.get_current_context()
        test = ctx.meta["test_list"]
        assert test == test_list
        assert test == [1, 2, 3]

    runner = CliRunner()
    result = runner.invoke(cli, ["-T", "1,2,3"])
    assert_click_runner_result(result)


def test_list_float_option_empty():
    @click.command()
    @list_float_option("test-list", "T", "Test list")
    def cli(test_list):
        ctx = click.get_current_context()
        test = ctx.meta["test_list"]
        assert test is None

    runner = CliRunner()
    result = runner.invoke(cli, ["-T", " "])
    assert_click_runner_result(result)


def test_commands_with_config_1():
    # random test
    @click.command(
        cls=ConfigCommand, entry_point_group="bob.extension.test_config_load"
    )
    def cli(**kwargs):
        pass

    runner = CliRunner()
    result = runner.invoke(cli, ["basic_config"])
    assert_click_runner_result(result)


def test_commands_with_config_2():
    # test option with valid default value
    @click.command(
        cls=ConfigCommand, entry_point_group="bob.extension.test_config_load"
    )
    @click.option("-a", cls=ResourceOption)
    def cli(a, **kwargs):
        assert type(a) == int, (type(a), a)
        click.echo("{}".format(a))

    runner = CliRunner()

    result = runner.invoke(cli, ["basic_config"])
    assert_click_runner_result(result)
    assert result.output.strip() == "1", result.output

    result = runner.invoke(cli, ["-a", 2])
    assert_click_runner_result(result)
    assert result.output.strip() == "2", result.output

    result = runner.invoke(cli, ["-a", 3, "basic_config"])
    assert_click_runner_result(result)
    assert result.output.strip() == "3", result.output

    result = runner.invoke(cli, ["basic_config", "-a", 3])
    assert_click_runner_result(result)
    assert result.output.strip() == "3", result.output


def test_commands_with_config_3():
    # test required options
    @click.command(
        cls=ConfigCommand, entry_point_group="bob.extension.test_config_load"
    )
    @click.option("-a", cls=ResourceOption, required=True)
    def cli(a, **kwargs):
        click.echo("{}".format(a))

    runner = CliRunner()

    result = runner.invoke(cli, [])
    assert_click_runner_result(result, exit_code=2)

    result = runner.invoke(cli, ["basic_config"])
    assert_click_runner_result(result)
    assert result.output.strip() == "1", result.output

    result = runner.invoke(cli, ["-a", 2])
    assert_click_runner_result(result)
    assert result.output.strip() == "2", result.output

    result = runner.invoke(cli, ["-a", 3, "basic_config"])
    assert_click_runner_result(result)
    assert result.output.strip() == "3", result.output

    result = runner.invoke(cli, ["basic_config", "-a", 3])
    assert_click_runner_result(result)
    assert result.output.strip() == "3", result.output


def test_prefix_aliasing():
    @click.group(cls=AliasedGroup)
    def cli():
        pass

    @cli.command()
    def test():
        click.echo("OK")

    @cli.command(name="test-aaa")
    def test_aaa():
        click.echo("AAA")

    runner = CliRunner()
    result = runner.invoke(cli, ["te"], catch_exceptions=False)
    assert result.exit_code != 0, (result.exit_code, result.output)

    result = runner.invoke(cli, ["test"], catch_exceptions=False)
    assert_click_runner_result(result)
    assert "OK" in result.output, (result.exit_code, result.output)

    result = runner.invoke(cli, ["test-a"], catch_exceptions=False)
    assert_click_runner_result(result)
    assert "AAA" in result.output, (result.exit_code, result.output)


def _assert_config_dump(ref, ref_date):
    today = time.strftime("%d/%m/%Y")
    # uncomment below to re-write tests
    # open(ref, 'wt').write(open('TEST_CONF').read())
    with open("TEST_CONF", "r") as f, open(ref, "r") as f2:
        text = f.read()
        ref_text = f2.read()
    ref_text = ref_text.replace(ref_date, today)
    # remove the starting and final whitespace of each line so the tests are more relaxed
    text = "\n".join(line.strip() for line in text.splitlines())
    ref_text = "\n".join(line.strip() for line in ref_text.splitlines())
    # replace ''' with """ so tests are more relaxed
    text = text.replace("'''", '"""')
    ref_text = ref_text.replace("'''", '"""')
    assert text == ref_text


def test_config_dump():
    @click.group(cls=AliasedGroup)
    def cli():
        pass

    @cli.command(cls=ConfigCommand, epilog="Examples!")
    @click.option(
        "-t",
        "--test",
        required=True,
        default="/my/path/test.txt",
        help="Path leading to test blablabla",
        cls=ResourceOption,
    )
    @verbosity_option(cls=ResourceOption)
    def test(config, test, **kwargs):
        """Test command"""
        pass

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli, ["test", "-H", "TEST_CONF"], catch_exceptions=False
        )
        ref = pkg_resources.resource_filename(
            "bob.extension", "data/test_dump_config.py"
        )
        assert_click_runner_result(result)
        _assert_config_dump(ref, "19/05/2022")


def test_config_dump2():
    @click.group(cls=AliasedGroup)
    def cli():
        pass

    @cli.command(
        cls=ConfigCommand, entry_point_group="bob.extension.test_dump_config"
    )
    @click.option(
        "--database",
        "-d",
        required=True,
        cls=ResourceOption,
        entry_point_group="bob.extension.test_dump_config",
        help="bla bla bla",
    )
    @click.option(
        "--annotator",
        "-a",
        required=True,
        cls=ResourceOption,
        entry_point_group="bob.extension.test_dump_config",
        help="bli bli bli",
    )
    @click.option(
        "--output-dir",
        "-o",
        required=True,
        cls=ResourceOption,
        help="blo blo blo",
    )
    @click.option(
        "--force", "-f", is_flag=True, cls=ResourceOption, help="lalalalalala"
    )
    @click.option(
        "--array",
        type=click.INT,
        default=1,
        cls=ResourceOption,
        help="lililili",
    )
    @click.option(
        "--database-directories-file",
        cls=ResourceOption,
        default="~/databases.txt",
        help="lklklklk",
    )
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
            cli, ["test", "-H", "TEST_CONF"], catch_exceptions=False
        )
        ref = pkg_resources.resource_filename(
            "bob.extension", "data/test_dump_config2.py"
        )
        assert_click_runner_result(result)
        _assert_config_dump(ref, "19/05/2022")


def test_config_command_with_callback_options():
    @click.command(
        cls=ConfigCommand, entry_point_group="bob.extension.test_config_load"
    )
    @verbosity_option(cls=ResourceOption, envvar="VERBOSE")
    @click.pass_context
    def cli(ctx, **kwargs):
        verbose = ctx.meta["verbosity"]
        assert verbose == 2, verbose

    runner = CliRunner()
    result = runner.invoke(cli, ["verbose_config"], catch_exceptions=False)
    assert_click_runner_result(result)

    runner = CliRunner(env=dict(VERBOSE="1"))
    result = runner.invoke(cli, ["verbose_config"], catch_exceptions=False)
    assert_click_runner_result(result)

    runner = CliRunner(env=dict(VERBOSE="2"))
    result = runner.invoke(cli, catch_exceptions=False)
    assert_click_runner_result(result)


def test_resource_option():
    # tests of ResourceOption used with ConfigCommand are done in other tests.

    # test usage without ConfigCommand and with entry_point_group
    @click.command()
    @click.option(
        "-a",
        "--a",
        cls=ResourceOption,
        entry_point_group="bob.extension.test_config_load",
    )
    def cli(a):
        assert a == 1, a

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["-a", "bob.extension.data.resource_config2"],
        catch_exceptions=False,
    )
    assert_click_runner_result(result)

    # test usage without ConfigCommand and without entry_point_group
    # should raise a TypeError
    @click.command()
    @click.option("-a", "--a", cls=ResourceOption)
    def cli(a):
        raise ValueError("Should not have reached here!")

    runner = CliRunner()
    result = runner.invoke(cli, ["-a", "1"], catch_exceptions=True)
    assert_click_runner_result(result, exit_code=1, exception_type=TypeError)

    # test ResourceOption with string_exceptions
    @click.command()
    @click.option(
        "-a",
        "--a",
        cls=ResourceOption,
        string_exceptions=("bob.extension.data.resource_config2"),
        entry_point_group="bob.extension.test_config_load",
    )
    def cli(a):
        assert a == "bob.extension.data.resource_config2", a

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["-a", "bob.extension.data.resource_config2"],
        catch_exceptions=False,
    )
    assert_click_runner_result(result)
