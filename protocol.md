# Protocol and connection model

WSRPC is a bidirectional RPC protocol carried by WebSocket text messages.
Both peers can register routes and initiate calls. Replies carry the call's
identifier, allowing independent requests to complete in a different order.
It uses JSON envelopes with `id`, `method`, `params`, `result` and `error`.
These examples describe WSRPC's protocol; they do not imply full JSON-RPC 2.0
compatibility.

## Requests and replies

A request names a method and supplies its parameters:

```json
{"id": 3, "method": "calculator.add", "params": {"a": 20, "b": 22}}
```

Successful replies echo the request identifier:

```json
{"id": 3, "result": 42}
```

A failed method call returns an error payload:

```json
{"id": 3, "error": {"type": "ValueError", "message": "Invalid value"}}
```

The TypeScript peer rejects remote failures with `RemoteError` while
preserving their payload. Python peers turn remote errors into `ClientException`. Local timeout and
transport exceptions are separate from a remote handler failure. Outgoing
Python calls accept keyword arguments. The receivers also understand positional
parameter arrays from other peers.

A connection can receive a new call while a local handler awaits a reverse
call to the remote side. The read loop must continue processing replies in
that situation. See the [aiohttp callback example](aiohttp/01-introduction.md#server-to-client-calls)
and the [ASGI callback example](asgi/01-introduction.md#reverse-calls-and-events).

```{image} _static/explanation.svg
:alt: Independent requests and replies over one WebSocket connection
```

## Events and binary messages

An object without an `id` is an application event delivered to registered
event listeners. Use `emit()` when no RPC reply is needed.

Raw binary WebSocket messages are separate from the JSON RPC envelopes.
Binary hooks receive transport-specific input: `aiohttp.WSMessage` in the
aiohttp implementation and `bytes` in the ASGI implementation, and `Uint8Array` in TypeScript. Bytes nested
inside a Python JSON value are base64-encoded by its default serializer.
TypeScript uses native `JSON.stringify`; agree on a codec or use raw binary
frames when exchanging byte arrays across languages.

## Routes and keepalive

Functions receive the RPC connection as their first argument. Route classes
attach state to one connection and expose methods through a policy such as
`Route`, `AllowedRoute`, `PrefixRoute` or `WebSocketRoute`.

A route object is created lazily. Calling its bare registered name invokes
its exposed `init` method; that call is explicit. Private names and methods
masked with `noproxy` remain inaccessible remotely.

The built-in `ping` route echoes its parameters. Application-level RPC ping
is separate from WebSocket PING/PONG frames, which ASGI servers handle at the
transport level. See each implementation's configuration for keepalive,
concurrency and timeout behavior.
