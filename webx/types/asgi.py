from typing import (
    Callable,
    Awaitable,
    Dict,
    Any
)


Scope = Dict[str, Any]
Receive = Callable[[], Awaitable]
Send = Callable[[], Awaitable]