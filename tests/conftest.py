from typing import Any
from unittest.mock import AsyncMock

import pytest

from eventcatch import extraction


class _FakeUsage:
    def __init__(self, input_tokens: int = 10, output_tokens: int = 10) -> None:
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class _FakeToolBlock:
    def __init__(self, data: dict[str, Any]) -> None:
        self.input = data


class _FakeResponse:
    def __init__(self, data: dict[str, Any]) -> None:
        self.content = [_FakeToolBlock(data)]
        self.usage = _FakeUsage()


@pytest.fixture
def fake_claude(monkeypatch: pytest.MonkeyPatch):
    """Patch the Anthropic client used by extraction.py to return canned tool input."""

    def _install(data: dict[str, Any]) -> AsyncMock:
        fake_client = AsyncMock()
        fake_client.messages.create.return_value = _FakeResponse(data)
        monkeypatch.setattr(extraction, "get_client", lambda: fake_client)
        return fake_client

    return _install
