"""
These are integration tests that need live sandbox and active Loki Server
"""

import pytest
from pytest import fixture
from cloudshell.sandbox_rest.sandbox_api import SandboxRestApiSession
from cloudshell.api.cloudshell_api import CloudShellAPISession
from driver import LokiGrafanaServerDriver


@fixture
def sandbox_api():
    return SandboxRestApiSession("localhost", "admin", "admin")


@fixture
def automation_api():
    return CloudShellAPISession("localhost", "admin", "admin", "Global")


@fixture
def sandbox_id():
    return "f66755c0-74c0-4e1a-9a45-7a5ae921bda9"


@fixture
def driver():
    return LokiGrafanaServerDriver()


def test_get_sandbox_events(driver, automation_api, sandbox_api, sandbox_id):
    events = driver._get_latest_events(automation_api, sandbox_api, sandbox_id)
    assert isinstance(events, list)
