from __future__ import annotations

import traceback
from typing import List, TYPE_CHECKING

from webx.http.response import BaseResponse
from webx.views.models import _RegisteredView

if TYPE_CHECKING:
    from webx.types.asgi import (
        Scope,
        Receive,
        Send
    )


class _LifespanEnclosure:
    def __init__(self, engine):
        self._engine = engine
    
    async def __aenter__(self):
        await self._engine.startup()
    
    async def __aexit__(self, *_):
        await self._engine.shutdown()

class ASGIEngine:
    """
    An engine class to handle ASGI
    """
    def __init__(self):
        self.views: List[_RegisteredView] = []
        self._enclosure = _LifespanEnclosure(self)

    async def startup(self):
        print("Startup operations")
    
    async def shutdown(self):
        print("Shutdown operations")
        
    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send
    ):
        print(scope)
        scopeT = scope["type"]
        assert scopeT in {"http", "websocket", "lifespan"}, "Scope type not supported"

        if scopeT == "lifespan":
            await self.handle_lifespan(scope, receive, send)
            return None

        for view in self.views:
            if view._match_scope(scope):
                args = view._extract_scope(scope)
                response = await view(*args)
                await response(scope, receive, send)
                return None

        # no view found, formulate a standard 404 response and send back.
        response = BaseResponse(status=404)
        await response(scope, receive, send)

    async def handle_lifespan(
        self,
        _scope: Scope,
        receive: Receive,
        send: Send
    ):
        print("Lifespan called")
        started = False
        await receive()
        try:
            async with self._enclosure:
                await send({"type": "lifespan.startup.complete"})
                started = True
                await receive()
        except Exception:
            exc = traceback.format_exc()
            if started is False:
                await send({"type": "lifespan.startup.failed", "message": exc})
            else:
                await send({"type": "lifespan.shutdown.failed", "message": exc})
            raise # re-raise so the exception can be logged to STDOUT
        else:
            await send({"type": "lifespan.shutdown.complete"})

        

app = ASGIEngine()
async def test(request):
    return BaseResponse(f"{request.host} {request.client} {request.secure}")

view = _RegisteredView(test, "/")
app.views.append(view)