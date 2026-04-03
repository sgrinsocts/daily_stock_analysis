from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

import fastapi.dependencies.utils
import fastapi.routing
import httpx
import starlette.concurrency
import starlette.routing


async def _patched_run_in_threadpool(func, *args, **kwargs):
    return func(*args, **kwargs)


@asynccontextmanager
async def _patched_contextmanager_in_threadpool(cm):
    resource = cm.__enter__()
    try:
        yield resource
    except Exception as exc:
        if not cm.__exit__(type(exc), exc, exc.__traceback__):
            raise
    else:
        cm.__exit__(None, None, None)


starlette.concurrency.run_in_threadpool = _patched_run_in_threadpool
starlette.routing.run_in_threadpool = _patched_run_in_threadpool
fastapi.routing.run_in_threadpool = _patched_run_in_threadpool
fastapi.dependencies.utils.run_in_threadpool = _patched_run_in_threadpool
fastapi.dependencies.utils.contextmanager_in_threadpool = _patched_contextmanager_in_threadpool


@dataclass
class SyncResponse:
    status_code: int
    headers: dict[str, str]
    content: bytes

    @property
    def text(self) -> str:
        return self.content.decode("utf-8")

    def json(self) -> Any:
        return json.loads(self.content.decode("utf-8"))


class SyncASGITestClient:
    """Sync-friendly ASGI client for test environments where TestClient hangs."""

    def __init__(self, app: Any, base_url: str = "http://testserver"):
        self.app = app
        self.base_url = base_url
        self._cookies = httpx.Cookies()

    async def _request_async(self, method: str, url: str, **kwargs: Any) -> tuple[int, dict[str, str], bytes]:
        transport = httpx.ASGITransport(app=self.app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url=self.base_url,
            cookies=self._cookies,
            follow_redirects=True,
        ) as client:
            response = await client.request(method, url, **kwargs)
            content = await response.aread()
            self._cookies = client.cookies
            return response.status_code, dict(response.headers), content

    def request(self, method: str, url: str, **kwargs: Any) -> SyncResponse:
        status_code, headers, content = asyncio.run(self._request_async(method, url, **kwargs))
        return SyncResponse(status_code=status_code, headers=headers, content=content)

    def get(self, url: str, **kwargs: Any) -> SyncResponse:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> SyncResponse:
        return self.request("POST", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> SyncResponse:
        return self.request("DELETE", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> SyncResponse:
        return self.request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> SyncResponse:
        return self.request("PATCH", url, **kwargs)

    def close(self) -> None:
        return None

    def __enter__(self) -> "SyncASGITestClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
