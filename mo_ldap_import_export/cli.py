# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Command-line interface."""

import os

import typer
from more_itertools import one

from .config import AuthBackendEnum
from .config import Settings


def generate_ldapsearch_command() -> list[str]:
    """Generate an ldapsearch command from the ingration configuration."""
    settings = Settings()
    command = ["ldapsearch"]
    # Output in LDIF format without comments and version
    command.append("-LLL")
    # LDAP authentication schemes are specified by RFC4513, with Simple Bind being
    # specified in section 5.1(.3) and SASL in section 5.2, while being further detailed
    # in RFC4422.
    #
    # Currently the LDAP integration does not support SASL, and as such the only
    # standardized way to connect to an LDAP server with the integration is Simple Bind.
    #
    # However the integration does support connecting using NTLM, a proprietary
    # Microsoft authentication mechanism, not specified by any RFC or similar standard.
    # NTLM can be used in two ways; As an authentication backend in SASL and via the
    # standard conflicting NTLM-over-Simple-Bind scheme.
    #
    # The integration only supports NTLM-over-Simple-Bind, which works by doing two
    # subsequent Simple Bind calls, sending an NTLM Negotiate message as in password
    # field during the first Simple Bind call, expecting the Active Directory server
    # to detect this payload and respond with an LDAP_INVALID_CREDENTIALS error
    # containing the NTLM Challenge in the error message field, upon which the client
    # can answer the challenge and send a new Simple Bind call with the NTLM
    # Authenticate message as the password.
    #
    # Unfortunately this NTLM-over-Simple-Bind behavior is not supported by ldapsearch,
    # as it is entirely non-standard, and as such we cannot generate a command for it.
    #
    # In theory we could generate a command for NTLM over SASL, however this
    # authentication mechanism is disabled by default for being unsafe as NTLM itself is
    # considered unsafe.
    # Why NTLM is disabled by default, while NTLM-over-Simple-Bind is not when they are
    # functionally equivalent is a question that only the engineers at Microsoft may
    # answer, but it is likely for backwards compatability.
    #
    # An attempt was also made to do authentication via DIGEST-MD5 over SASL using
    # ldapsearch as an alternative to NTLM as Active Directory reports DIGEST-MD5 as a
    # valid authentication scheme, however using DIGEST-MD5 always results in an
    # LDAP_INVALID_CREDENTIALS error even if the provided credentails are valid.
    # Why DIGEST-MD5 is included in the list of authentication schemes when it is
    # functionally disabled by default is a question that only the engineers at
    # Microsoft may answer, but it is likely for backwards compatability.
    #
    # It might be possible to extend this code to support Kerberos over SASL in the
    # future, however for now, we can only generate the ldapsearch command if the server
    # allows standard compliant Simple Bind.
    assert (
        settings.ldap_auth_method == AuthBackendEnum.SIMPLE
    ), f"Can only generate script for {AuthBackendEnum.SIMPLE}"
    command.append("-x")
    # Configure connection string
    assert (
        len(settings.ldap_controllers) == 1
    ), "Cannot generate script for multiple LDAP controllers"
    ldap_controller = one(settings.ldap_controllers)
    ldap_url = "ldaps://" if ldap_controller.use_ssl else "ldap://"
    ldap_url += ldap_controller.host
    if ldap_controller.port:
        ldap_url += ":" + str(ldap_controller.port)
    command.append("-H")
    command.append(f'"{ldap_url}"')
    # Configure timeout
    command.append("-o")
    command.append(f"nettimeout={ldap_controller.timeout}")
    # Configure username
    command.append("-D")
    command.append(f'"{settings.ldap_user}"')
    # Configure password
    command.append("-w")
    command.append(f'"{settings.ldap_password.get_secret_value()}"')
    # Configure search base
    command.append("-b")
    command.append(f'"{settings.ldap_search_base}"')
    return command


def commandlist_to_string(command: list[str]) -> str:
    return " ".join(command)


ldapsearch = typer.Typer()


@ldapsearch.command()
def generate() -> None:
    """Generate and print the ldapsearch command."""
    print(commandlist_to_string(generate_ldapsearch_command()))


@ldapsearch.command()
def run(
    extra: list[str] | None = typer.Argument(
        None, help="Extra arguments to be added to the end of the command."
    ),
) -> None:
    """Generate and run the ldapsearch command."""
    # Ensure that extra is always a list
    extra = extra or []
    # This intentionally uses `os.system` instead of the recommended `subprocess.run`
    # as we understand the risks involved and do in fact want shell interpretation of
    # the 'extra' arguments, etc. We want this command to behave as closely as possible
    # to using the generate command followed by running the command yourself.
    #
    # The main goal of this command is providing the convenience of not having to copy
    # and paste the command generated by the generate command, as copy and paste can be
    # broken in some environments, especially in Citrix.
    os.system(commandlist_to_string(generate_ldapsearch_command() + extra))


cli = typer.Typer()
cli.add_typer(
    ldapsearch, name="ldapsearch", help="Commands related to the ldapsearch program."
)


if __name__ == "__main__":  # pragma: no cover
    cli()
