# Routes and TypeScript API

`wsrpc-ts` implements the same bidirectional WSRPC protocol as the Python
servers. Use Node HTTP, Express or Fastify with `ws`, or connect an existing
accepted `ws` socket to the RPC endpoint. The library supports Node.js 22+;
the standalone `.ts` examples in this guide use Node.js 24+.

Start with the framework tabs in the [JavaScript quick start](../javascript/quick-start.md).
Every server example is one complete `app.ts` file. It includes `echo`, a
reverse `callback`, an ordinary HTTP health route and shutdown handling.

## Install from a checkout

The monorepository contains `@wsrpc/client` and `@wsrpc/server`. The browser
client is the existing `wsrpc-js-client`, with its original API and Git history.
Build both archives from a `wsrpc-ts` checkout:

```shell
cd /path/to/wsrpc-ts
npm ci
npm run pack
```

In your application directory, install both archives:

```shell
npm install /path/to/wsrpc-ts/artifacts/wsrpc-client-4.5.0.tgz /path/to/wsrpc-ts/artifacts/wsrpc-server-4.5.0.tgz
# For an Express or Fastify application, also install its framework:
# npm install express
# npm install fastify
```

These commands work before publication. After release, use
`npm install @wsrpc/client @wsrpc/server`. Both versions are derived from the
same GitHub Release tag; version 4.5.0 continues the existing client's 4.4.1
series. Copy the selected server from the quick start to `app.ts` and run
`node app.ts`. For static checking, install TypeScript and the Node/framework
declaration packages in your application and use your normal TypeScript build.

The browser client uses `import WSRPC from '@wsrpc/client'`, CommonJS
`require('@wsrpc/client')`, or the classic `dist/wsrpc.min.js` script. Its
module and distribution paths remain available. The Node client is a separate
entry, `import { WSRPCClient } from '@wsrpc/client/node'`. Core routes, errors
and protocol types are exported through `@wsrpc/client/core` and re-exported
by `@wsrpc/server`.

## Register methods and serve connections

```typescript
import { createServer } from 'node:http';
import { WebSocketAsync } from '@wsrpc/server';

class RPC extends WebSocketAsync {}
RPC.addRoute('add', (_socket, { a, b }: { a: number; b: number }) => a + b);

const http = createServer((_request, response) => response.end('HTTP works'));
const rpc = RPC.attach(http, { path: '/ws/' });
http.listen(8000, '127.0.0.1');
```

`attach()` adds one HTTP upgrade listener and preserves ordinary HTTP handling.
The RPC path is exact, including its trailing slash. Other upgrade listeners
can handle other paths. Express uses its HTTP server; Fastify uses
`app.server`. For accepted sockets, create `const rpc = RPC.asServer()` once
and call `rpc.serve(webSocket)` for each connection. The returned `RPCPeer`
provides calls, context, lifecycle signals and a connection abort signal.

Create a separate `WebSocketAsync` subclass per application. Each RPCServer
snapshots that class's route registrations when created, and exposes its
active `clients` map. Register application routes before `attach()` or
`asServer()`; `peer.addRoute()` changes only that peer's routes.

Call `await rpc.close()` before stopping the parent HTTP server. The Fastify
example does this in `preClose`. Shutdown detaches the upgrade listener,
aborts pending authorization, rejects unanswered RPC calls and closes sockets.
It does not take ownership of the parent HTTP server.

## Typed calls and callbacks

Functions receive `(socket, params)`. Object parameters are passed as one
object and arrays stay arrays; use object destructuring for the equivalent
of Python keyword arguments. Missing/null parameters become `{}`. An
undefined return value becomes JSON null. Both synchronous and async handlers
are supported, with all JavaScript execution on the Node event loop.

`await socket.call('double', { value: 21 })` works with the existing Python
and browser clients. `socket.proxy` provides dynamic dotted calls. Apply an
interface to obtain checked arguments and results:

```typescript
import type { RPCPeer } from '@wsrpc/server';

interface Remote {
  counter: {
    add(params: { value: number }): number;
  };
}

async function increment(socket: RPCPeer): Promise<number> {
  return socket.remote<Remote>().counter.add({ value: 2 });
}
```

The generic contract checks nested method names, argument shapes and results.
Synchronous and async return types both become Promises. Methods can have no
parameters, optional parameters or one required params object. The wire protocol
carries a single params value, so multi-argument signatures are not exposed by
the typed proxy. Pass call options after params, for example
`remote.counter.add({ value: 2 }, { timeout: 5000 })`.

TypeScript contracts are compile-time checks; handlers validate incoming data.
Each call returns an independent Promise, so replies can arrive out of order.
Handlers can await reverse calls while other messages continue to be processed.
For a complete client with callbacks, see {ref}`typescript-client`.

## Route classes and connection state

```typescript
import { AllowedRoute, WebSocketAsync } from '@wsrpc/server';

class Counter extends AllowedRoute {
  value = 0;

  init({ value = 0 }: { value?: number }) {
    this.value = value;
    return this.value;
  }

  add({ value }: { value: number }) {
    this.value += value;
    return this.value;
  }

  override _onClose() {
    // Release resources owned by this connection.
  }
}

class RPC extends WebSocketAsync {}
RPC.addRoute('counter', Counter);
```

A route object is created lazily for each connection. Calling `counter`
explicitly invokes `init`; `counter.add` does not implicitly call it.
`AllowedRoute` and `WebSocketRoute` expose public prototype methods, excluding
private names, constructors, getters, instance fields and Object methods.
`noproxy(Counter.prototype.someMethod)` masks a public method. `Route` uses
an explicit static `methods` set or methods decorated with `@proxy`. `PrefixRoute` exposes `rpc_name` as `name`
and supports an overridable static `prefix`. TypeScript's `private` modifier is
erased; use `#private`, underscore-prefixed names or `noproxy` for runtime
masking. Standard `@proxy`/`@noproxy` method decorators require a TypeScript
build; Node's native type stripping does not transform decorators.

## Pre-created routes and implicit context

A Route class is instantiated lazily once per connection. An already initialized
Route object keeps its dependencies and shares its application state across
connections:

```typescript
import { AllowedRoute, getCurrentSocket, WebSocketAsync } from '@wsrpc/server';

function connectionId(): string {
  return getCurrentSocket().id;
}

class Service extends AllowedRoute {
  calls = 0;
  constructor(readonly prefix: string) { super(); }
  async echo({ value }: { value: number }) {
    this.calls++;
    const before = this.socket.id;
    await Promise.resolve();
    return { value, prefix: this.prefix, sameConnection: before === connectionId() };
  }
  async callback({ value }: { value: number }) {
    return this.socket.call<number>('double', { value });
  }
}

class RPC extends WebSocketAsync {}
RPC.addRoute('service', new Service('configured'));
```

Create shared objects without a socket constructor argument. `this.socket`
resolves the connection using Node's AsyncLocalStorage: concurrent calls from
different connections do not overwrite a field on the shared object. It remains
correct through `await` and reverse callbacks. Ordinary helper functions can
use `getCurrentSocket()` and `getCurrentCall()` without receiving a socket
argument; these throw outside an active RPC context. Authentication data is
available through `getCurrentSocket().context`. Plain function handlers also
have the peer bound as `this`; arrow functions use their explicit socket
argument.

`_onClose()` runs once per connection that used an instance, with that
connection's context. It releases connection resources. Dispose shared
application resources at application shutdown. Keep background jobs outside
request lifetimes and pass any context they need explicitly. Method exposure
policies apply equally to classes and registered objects.

## Events, binary frames, signals and broadcast

`await peer.emit({ topic: 'changed', value: 42 })` sends an event with no RPC
reply. Events cannot contain `id`. Receive events with
`peer.onEvent.connect(listener)`. Send a binary WebSocket frame with
`peer.sendRaw(new Uint8Array(...))`; `onBinary` receives `Uint8Array` values.
The shared [protocol guide](../protocol.md) explains binary versus JSON data.

`rpc.broadcast(method, params, options)` calls every current client and
returns `PromiseSettledResult[]`, preserving failures for individual peers.
Connections and broadcasts are local to one process.

Signals use `connect(listener)` and return an unsubscribe function:

| Object | Signals |
| --- | --- |
| RPCServer | `onConnect`, `onDisconnect`, `onError` |
| RPCPeer | `onCallStart`, `onCallSuccess`, `onCallFail`, `onEvent`, `onBinary`, `onClose`, `onError` |

Call signals include the peer, request id, method and params; completion
signals add the result or error. Listener failures are reported through
`onError` without suppressing replies or pending-call cleanup. Close hooks
are awaited, so keep them finite. A running handler observes `peer.signal`
when its connection closes; JavaScript cannot forcibly cancel arbitrary work.

## Authorization and limits

Supply `authorize(request, signal)` in `attach()` options. It runs before
the upgrade, returns false to deny with HTTP 403, and otherwise supplies
`peer.context`. Its signal aborts on disconnect, authorization timeout or
server shutdown. HTTP middleware does not automatically authorize upgrades.

| Option | Default | Meaning |
| --- | --- | --- |
| `path` | `/ws/` | Exact upgrade URL path |
| `timeout` | 30000 | Outgoing RPC timeout, milliseconds |
| `maxPendingCalls` | 1024 | Unanswered outgoing calls per peer |
| `maxConcurrentCalls` | 128 | Running incoming handlers per peer |
| `maxPayload` | 1048576 | Incoming WebSocket message bytes |
| `maxBufferedBytes` | 1048576 | Queued outgoing message bytes |
| `authorizationTimeout` | 10000 | Milliseconds before aborting authorization |
| `closeTimeout` | 1000 | Milliseconds before terminating a closing socket |

`call()` also takes `{ timeout, signal }` as its third argument. Timeout zero
disables the local deadline. Aborting or timing out a call removes its pending
entry; the wire protocol has no message to cancel the remote handler. Late
replies are ignored. WebSocket control frames are handled by `ws`; RPC `ping`
independently echoes its params.

## Errors and JSON codecs

Remote errors reject with `RemoteError` (`ClientException` is an alias); its
`payload` preserves the remote value. Local failures use `CallTimeoutError`,
`ConnectionClosedError` or `CapacityError`. Closing a connection rejects all
pending calls. Invalid JSON/identifiers and duplicate in-flight IDs close the
connection. Stack traces are not sent as error payloads.

Default JSON uses native `JSON.parse` and `JSON.stringify`. Supply a
`codec: { loads, dumps }` to customize it. BigInt and cyclic values fail
serialization. Embedded byte arrays are not automatically converted to
Python's base64 representation; use raw binary frames or an agreed codec.

## Verification and development

In the `wsrpc-ts` checkout:

```shell
npm run check
npm run test:interop
npm run pack
```

The Node suite exercises the original JS client, Node HTTP/Express/Fastify,
concurrency, callbacks, route policies, authorization, limits and cleanup.
Interoperability uses a locked uv environment and real connections in both
directions with `wsrpc-aiohttp` and `wsrpc-asgi`. The shared documentation
checks TypeScript syntax without requiring the unpublished package. See
[maintaining the documentation](../contributing.md) for its optional runtime
checks against the locally built npm artifact.
