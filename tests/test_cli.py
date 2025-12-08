# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from mo_ldap_import_export.cli import cli

runner = CliRunner()


def test_cli() -> None:
    result = runner.invoke(cli, [])
    assert result.exit_code == 2
    expected_output = [
        "Usage: root [OPTIONS] COMMAND [ARGS]...",
        "Try 'root --help' for help.",
        "Missing command.",
    ]
    for expected in expected_output:
        assert expected in result.output


def test_help() -> None:
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    expected_output = [
        "Usage: root [OPTIONS] COMMAND [ARGS]...",
        "--help                        Show this message and exit.",
        "ldapsearch   Commands related to the ldapsearch program.",
    ]
    for expected in expected_output:
        assert expected in result.output


def test_ldapsearch() -> None:
    result = runner.invoke(cli, ["ldapsearch"])
    assert result.exit_code == 2
    expected_output = [
        "Usage: root ldapsearch [OPTIONS] COMMAND [ARGS]...",
        "Try 'root ldapsearch --help' for help.",
        "Missing command.",
    ]
    for expected in expected_output:
        assert expected in result.output


def test_ldapsearch_help() -> None:
    result = runner.invoke(cli, ["ldapsearch", "--help"])
    assert result.exit_code == 0
    expected_output = [
        "Usage: root ldapsearch [OPTIONS] COMMAND [ARGS]...",
        "Commands related to the ldapsearch program.",
        "--help          Show this message and exit.",
        "generate   Generate and print the ldapsearch command.",
        "run        Generate and run the ldapsearch command.",
    ]
    for expected in expected_output:
        assert expected in result.output


def test_ldapsearch_generate_help() -> None:
    result = runner.invoke(cli, ["ldapsearch", "generate", "--help"])
    assert result.exit_code == 0
    expected_output = [
        "Usage: root ldapsearch generate [OPTIONS]",
        "Generate and print the ldapsearch command.",
        "--help          Show this message and exit.",
    ]
    for expected in expected_output:
        assert expected in result.output


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
def test_ldapsearch_generate_invalid_auth() -> None:
    result = runner.invoke(cli, ["ldapsearch", "generate"])
    assert result.exit_code == 1
    assert "Can only generate script for AuthBackendEnum.SIMPLE" in str(
        result.exception
    )


GENERATE_EXPECTED_OUTPUT = [
    "ldapsearch",
    "-LLL",
    "-x",
    "-H",
    '"ldap://localhost"',
    "-o",
    "nettimeout=5",
    "-D",
    '"foo"',
    "-w",
    '"foo"',
    "-b",
    '"DC=ad,DC=addev"',
]


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
@pytest.mark.envvar({"LDAP_AUTH_METHOD": "simple"})
def test_ldapsearch_generate() -> None:
    result = runner.invoke(cli, ["ldapsearch", "generate"])
    assert result.exit_code == 0
    expected = " ".join(GENERATE_EXPECTED_OUTPUT) + "\n"
    assert result.output == expected


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
@pytest.mark.envvar(
    {
        "LDAP_AUTH_METHOD": "simple",
        "LDAP_CONTROLLERS": '[{"host": "localhost", "use_ssl": true}]',
    }
)
def test_ldapsearch_generate_with_ldaps() -> None:
    result = runner.invoke(cli, ["ldapsearch", "generate"])
    assert result.exit_code == 0
    expected_output = [
        '"ldaps://localhost"' if x == '"ldap://localhost"' else x
        for x in GENERATE_EXPECTED_OUTPUT
    ]
    expected = " ".join(expected_output) + "\n"
    assert result.output == expected


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
@pytest.mark.envvar(
    {
        "LDAP_AUTH_METHOD": "simple",
        "LDAP_CONTROLLERS": '[{"host": "localhost", "port": 1337}]',
    }
)
def test_ldapsearch_generate_with_port() -> None:
    result = runner.invoke(cli, ["ldapsearch", "generate"])
    assert result.exit_code == 0
    expected_output = [
        '"ldap://localhost:1337"' if x == '"ldap://localhost"' else x
        for x in GENERATE_EXPECTED_OUTPUT
    ]
    expected = " ".join(expected_output) + "\n"
    assert result.output == expected


def test_ldapsearch_run_help() -> None:
    result = runner.invoke(cli, ["ldapsearch", "run", "--help"])
    assert result.exit_code == 0
    expected_output = [
        "Usage: root ldapsearch run [OPTIONS] [EXTRA]",
        "Generate and run the ldapsearch command.",
        "--help          Show this message and exit.",
    ]
    for expected in expected_output:
        assert expected in result.output


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
@pytest.mark.envvar({"LDAP_AUTH_METHOD": "simple"})
async def test_ldapsearch_run() -> None:
    with patch("os.system") as os_system:
        result = runner.invoke(cli, ["ldapsearch", "run"])
        assert result.exit_code == 0
        assert result.output == ""

    expected = " ".join(GENERATE_EXPECTED_OUTPUT)
    os_system.assert_called_once_with(expected)
