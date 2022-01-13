from __future__ import annotations

import inspect
from typing import (
    Callable,
    Awaitable,
    Optional,
    Tuple,
    Any,
    TYPE_CHECKING
)

from webx.http.response import BaseResponse
from webx.http.request import HttpRequest
from webx.core.exceptions import InvalidView

if TYPE_CHECKING:
    from webx.types.asgi import (
        Scope,
        Receive,
        Send
    )
    from inspect import FullArgSpec


class _RegisteredView:
    """
    Represents a registered view object.
    The ASGI Engine has access to these, and can call them at any time.
    """

    def __init__(
        self,
        callback: Callable[[], Awaitable],
        path: str,
        *,
        name: Optional[str] = None,
        view_type: str = "http" # could be websocket. defaults to http
    ):
        self.callback = callback
        self.path = path
        self.name = name
        self._type = view_type

        self.arg_spec: FullArgSpec = inspect.getfullargspec(callback)

        if len(self.arg_spec.args) == 0:
            raise InvalidView("'request' parameter missing in view declaration")
    
    def _match_scope(self, scope: Scope) -> bool:
        scopeT = scope["type"]
        if scopeT == self._type:
            # the scope type matches. next check for the path
            scope_path = scope["path"]
            if scope_path == self.path:
                return True

        return False
    
    def _extract_scope(self, scope: Scope) -> Tuple[HttpRequest, ...]:
        # Extract elements from the scope that it may need
        # And construct a HttpRequest object to pass through.

        # Then construct the other arguments to pass and return a tuple.

        request = HttpRequest.from_scope(scope)
        return (request,)
        

    async def __call__(
        self,
        *callback_args,
        **callback_kwargs
    ) -> BaseResponse:
        # handles running the view's callback
        # on error, returns an automated 500 response
        try:
            response = await self.callback(*callback_args, **callback_kwargs)
        except BaseException as exc:
            response = BaseResponse(
                content="Internal server error: {}".format(exc),
                status=500
            )

        return response