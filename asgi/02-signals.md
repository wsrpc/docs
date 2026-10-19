# Signals

Signals observe connections, authorization and calls. Receivers must be
`async def` functions. Attach them before creating the ASGI endpoint:

<!-- name: test_signals -->
```python
from wsrpc_asgi import WebSocketAsync


class RPC(WebSocketAsync):
    pass


async def on_call_success(method, serial, args, kwargs, result):
    print(method, result)


RPC.ON_CALL_SUCCESS.connect(on_call_success)
app = RPC.as_asgi()
```

| Signal | Keyword arguments |
| --- | --- |
| `ON_CONN_OPEN` | `socket`, `request` |
| `ON_AUTH_SUCCESS` | `socket`, `request` |
| `ON_AUTH_FAIL` | `socket`, `request` |
| `ON_CONN_FAIL` | `socket`, `request`, `err` |
| `ON_CONN_CLOSE` | `socket`, `request` |
| `ON_CALL_START` | `method`, `serial`, `args`, `kwargs` |
| `ON_CALL_SUCCESS` | `method`, `serial`, `args`, `kwargs`, `result` |
| `ON_CALL_FAIL` | `method`, `serial`, `args`, `kwargs`, `err` |

`socket` and `request` refer to the transport WebSocket: an `ASGIWebSocket`
for bare ASGI routes, or the supplied framework WebSocket for `serve()`.
`ON_CONN_OPEN` runs before authorization and acceptance. Authorization success
also precedes acceptance. `ON_CONN_FAIL` observes unexpected lifecycle/transport
failures. `ON_CONN_CLOSE` runs after cleanup, including rejected handshakes.

Receiver exceptions are logged and do not prevent other receivers from
running. Receivers are stored in a set, so their relative order is unspecified.
Each subclass copies its parent's signals; each `as_asgi()` application takes
another copy. Later changes to the original class do not mutate those copies.
`RPC.freeze()` prevents registering additional receivers on that class.

```python
from wsrpc_asgi.signal import Signal, receiver

signal: Signal[[int]] = Signal()


@receiver(signal)
async def changed(value: int):
    print(value)
```
