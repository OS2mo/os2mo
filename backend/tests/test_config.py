# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from mora.config import Settings


def test_amqp_defaults() -> None:
    settings = Settings()
    assert settings.amqp.get_url() == "amqp://guest:guest@msg_broker:5672/"


def test_amqp_new_syntax_whole_url(monkeypatch) -> None:
    monkeypatch.setenv("AMQP__URL", "amqp://foo:bar@example.com:1234/baz")
    settings = Settings()
    assert settings.amqp.get_url() == "amqp://foo:bar@example.com:1234/baz"


def test_amqp_new_syntax_individual_components(monkeypatch) -> None:
    monkeypatch.setenv("AMQP__URL__SCHEME", "amqp")
    monkeypatch.setenv("AMQP__URL__USER", "foo")
    monkeypatch.setenv("AMQP__URL__PASSWORD", "bar")
    monkeypatch.setenv("AMQP__URL__HOST", "example.com")
    monkeypatch.setenv("AMQP__URL__PORT", "1234")
    monkeypatch.setenv("AMQP__URL__VHOST", "baz")
    settings = Settings()
    assert settings.amqp.get_url() == "amqp://foo:bar@example.com:1234/baz"


def test_amqp_old_syntax_whole_url(monkeypatch) -> None:
    monkeypatch.setenv("AMQP_URL", "amqp://foo:bar@example.com:1234/baz")
    settings = Settings()
    assert settings.amqp.get_url() == "amqp://foo:bar@example.com:1234/baz"


def test_amqp_old_syntax_only_password(monkeypatch) -> None:
    monkeypatch.setenv("AMQP_PASSWORD", "hunter2")
    settings = Settings()
    assert settings.amqp.get_url() == "amqp://guest:hunter2@msg_broker:5672/"
