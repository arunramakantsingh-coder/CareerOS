from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class ConnectorCapabilities:
    read_messages: bool = False
    read_metadata: bool = False
    search_messages: bool = False
    read_threads: bool = False
    send_message: bool = False
    modify_messages: bool = False


@dataclass
class ConnectorHealth:
    provider: str
    status: str
    email_address: str | None = None
    capabilities: ConnectorCapabilities = field(default_factory=ConnectorCapabilities)
    scopes: list[str] = field(default_factory=list)
    token_expires_at: str | None = None
    last_sync_at: str | None = None
    last_sync_status: str | None = None
    error_code: str | None = None
    error_message: str | None = None


class EmailConnector(Protocol):
    """Common contract for Gmail, Microsoft Graph and future IMAP/SMTP connectors."""
    provider: str

    def capabilities(self) -> ConnectorCapabilities: ...
    async def connect(self, **kwargs: Any) -> Any: ...
    async def disconnect(self) -> Any: ...
    async def health_check(self) -> ConnectorHealth: ...
    async def sync(self, **kwargs: Any) -> Any: ...
    async def fetch_messages(self, **kwargs: Any) -> list[dict[str, Any]]: ...
    async def fetch_thread(self, thread_id: str) -> dict[str, Any]: ...
    async def search_messages(self, query: str, **kwargs: Any) -> list[dict[str, Any]]: ...
    async def get_metadata(self) -> dict[str, Any]: ...
    async def send_message(self, **kwargs: Any) -> Any: ...
    async def refresh_auth(self) -> Any: ...
