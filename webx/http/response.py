from __future__ import annotations

import json
from typing import (
    Dict,
    Optional,
    Any,
    List,
    Tuple,
    TYPE_CHECKING
)

if TYPE_CHECKING:
    from webx.types.asgi import (
        Scope,
        Receive,
        Send
    )


class BaseResponse:
    charset: str = "utf-8"
    media_type: Optional[str] = None

    body: Optional[bytes] = None

    def __init__(
        self,
        content: Any = None,
        status: int = 200,
        headers: Optional[Dict[str, Any]] = None,
        media_type: Optional[str] = None
    ):
        self.raw_content = content
        self.status = status
        self.headers = headers
        self.media_type = media_type or self.media_type

        self.body = self.render_content(content)
        self.raw_headers = self.render_headers(headers)

    def render_content(self, content: Any) -> bytes:
        # This method is responsible for
        # parsing given content into bytes to be sent across
        if content is None:
            return b""
        elif isinstance(content, bytes):
            return content
        
        return content.encode(self.charset)

    def render_headers(self, headers: dict) -> List[Tuple[bytes, bytes]]:
        raw_headers: List[Tuple[bytes, bytes]] = []
        parse_content_length = False
        parse_content_type = False

        if headers is None:
            parse_content_length, parse_content_type = True, True
        else:
            raw_headers = [
                (k.lower().encode("utf-8"), v.encode("utf-8"))
                for k, v in headers.items()
            ]
            parse_content_type = b"content-type" not in raw_headers
            parse_content_length = b"content-length" not in raw_headers

        # Any status code under 200, or in {203, 204} shouldn't need the content-... headers
        if self.status < 200 or self.status in {203, 204}:
            parse_content_length, parse_content_type = False, False
        
        if self.body is None:
            # if there's no body, we don't include a content-length
            parse_content_length = False
        
        if parse_content_length:
            cnt_length = str(len(self.body))
            raw_headers.append((b"content-length", cnt_length))
        
        _cnt_type = self.media_type
        if parse_content_type and _cnt_type is not None:
            if _cnt_type.startswith("text/"):
                _cnt_type += "; charset=" + self.charset

            raw_headers.append((b"content-type", _cnt_type))

        return raw_headers
    
    async def __call__(
        self,
        _scope: Scope,
        _receive: Receive,
        send: Send
    ):
        await send({
            "type": "http.response.start",
            "status": self.status,
            "headers": self.raw_headers
        })
        await send({
            "type": "http.response.body",
            "body": self.body
        })

class JsonResponse(BaseResponse):
    media_type = "application/json"

    def render_content(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":")
        ).encode(self.charset)