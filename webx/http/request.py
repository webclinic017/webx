from __future__ import annotations

from urllib.parse import parse_qsl
from typing import TYPE_CHECKING, Tuple

from webx.tooling.multidict import MultiDict, CaseInsensitiveMultiDict

if TYPE_CHECKING:
    from webx.types.asgi import Scope


class HttpRequest:
    def __init__(
        self,
        *,
        method: str,
        query: MultiDict,
        headers: CaseInsensitiveMultiDict,
        host: Tuple[str, int],
        client: Tuple[str, int],
        root_path: str,
        path: str,
        scheme: str
    ):
        self.method = method
        self.query = query
        self.headers = headers
        self.host = host
        self.client = client
        self.root_path = root_path
        self.path = path
        self.scheme = scheme

    @property
    def secure(self) -> bool:
        return self.scheme == "https"

    @classmethod
    def from_scope(cls, scope: Scope):
        qs: bytes = scope["query_string"]
        method: str = scope["method"].upper()
        headers: dict = scope["headers"]
        host: tuple = scope["server"]
        client: tuple = scope["client"]
        root_path: str = scope["root_path"]
        path: str = scope["path"]
        scheme: str = scope["scheme"]

        # Query parameters parsing
        qs = qs.decode("utf-8")

        qs_spec = parse_qsl(qs)
        query_params = MultiDict()

        for (k, v) in qs_spec:
            query_params[k] = v

        # Headers parsing
        ci_headers = CaseInsensitiveMultiDict()

        for header, value in headers:
            header, value = header.decode("utf-8"), value.decode("utf-8")
            ci_headers[header] = value

        return cls(
            method=method,
            query=query_params,
            headers=ci_headers,
            host=host,
            client=client,
            root_path=root_path,
            path=path,
            scheme=scheme
        )