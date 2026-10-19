# JavaScript / TypeScript clients

Use the existing browser client or the typed Node.js transport from
`@wsrpc/client`. Both connect to Python and Node servers.

(typescript-client)=
## TypeScript / Node.js

`@wsrpc/client/node` provides a typed `ws`-based `WSRPCClient`. It connects to the same
servers and supports callbacks, route classes, events and typed remote proxies.
Install the client and its optional Node transport (or use the local archives
from the [TypeScript guide](../typescript/index.md#install-from-a-checkout)):

```shell
npm install @wsrpc/client ws
# For type checking a Node application:
npm install --save-dev @types/ws @types/node
```

Browser and Worker consumers install only `@wsrpc/client`; it does not pull in
`ws` or Node declarations. Then run the Node client:

```{literalinclude} ../typescript/examples/client.ts
:language: typescript
```

Register callback routes through the `routes` option before connecting.
Close the client in `finally`. `client.call(method, params, options)` returns
a Promise; `client.remote<Contract>()` adds checked parameter and result types.
Timeout values are milliseconds in TypeScript, compared with seconds in Python.

## Browser

Install `@wsrpc/client` and serve its `dist/wsrpc.min.js` file through your
framework's static-file support. The script defines `window.WSRPC`. Python
packages also bundle the same client and declarations in `STATIC_DIR`.

```html
<script src="/js/wsrpc.min.js"></script>
<script>
  const scheme = window.location.protocol === "https:" ? "wss:" : "ws:";
  const rpc = new WSRPC(`${scheme}//${window.location.host}/ws/`);
  rpc.addRoute("double", ({ value }) => value * 2);
  rpc.connect();

  async function echo() {
    await rpc.onEvent("onconnect");
    try {
      console.log(await rpc.call("echo", { message: "Hello" }));
    } catch (error) {
      console.error(error);
    }
  }

  echo();
</script>
```

When using a bundler or ESM, import the default export:

```javascript
import WSRPC from "@wsrpc/client";
```

The original `wsrpc.es6.js`, `dist/wsrpc.js` and `dist/wsrpc.min.js` paths
remain available; CommonJS `require("@wsrpc/client")` returns the browser constructor.
Existing JavaScript clients use the same protocol with either server.

## Browser contracts in TypeScript

The existing constructor also accepts a generic contract. Its implementation and
JavaScript call signatures stay unchanged:

```typescript
import WSRPC from '@wsrpc/client';

interface Remote {
  echo(params: { value: number }): { value: number };
}
const rpc = new WSRPC<Remote>('ws://127.0.0.1:8000/ws/');
// Once connected, the proxy checks arguments and returns Promise<{ value: number }>.
// await rpc.proxy.echo({ value: 42 });
```

Browser call options use `{ noWait: true }`. Node clients instead accept
`{ timeout, signal }`; the type declarations keep these transport options distinct.
Both are checked by the repository's `npm run test:types`, including expected
compiler errors for incorrect calls.

## Observe browser payloads

Existing application code written for 4.4.1 keeps using `new WSRPC(url)` or
`new WSRPC(url, reconnectTimeout)`. Only applications which need tracing opt in
to the third constructor argument:

```javascript
const rpc = new WSRPC('ws://127.0.0.1:8000/ws/', 1000, {
  onFrame({ direction, data }) {
    console.log(direction, data); // "in" or "out", raw application payload
  },
});
rpc.connect();
```

Incoming payloads arrive before JSON parsing, including malformed JSON.
Outgoing payloads are reported once after WebSocket.send accepts them, including
queued calls when flushed, callback responses and `sendRaw` data. Control frames
are handled by the browser and are not exposed. This is observation only:
return values are ignored and Promises are never awaited. Metadata is frozen
and mutable binary payloads are copied. Observer failures, including rejected
Promises and failures in console.error, do not interrupt RPC. DEBUG and TRACE
retain their boolean behavior.

A compatibility test runs the same unmodified HTML/JavaScript application with
the original npm 4.4.1 bundle and the new bundle, comparing results from calls,
callbacks, events, binary sends, errors and reconnects. Unit tests also compare
the serialized messages against the original source and UMD release.
