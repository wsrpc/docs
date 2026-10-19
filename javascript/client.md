# JavaScript / TypeScript clients

Use the existing browser client or the typed Node.js transport from
`@wsrpc/client`. Both connect to Python and Node servers.

(typescript-client)=
## TypeScript / Node.js

`@wsrpc/client/node` provides a typed `ws`-based `WSRPCClient`. It connects to the same
servers and supports callbacks, route classes, events and typed remote proxies.
Install `@wsrpc/client` (or use the local archives described in the
[TypeScript guide](../typescript/index.md#install-from-a-checkout)), then run:

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
