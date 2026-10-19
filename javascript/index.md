# JavaScript / TypeScript

Two npm packages share one repository:

| Package | Use it for |
| --- | --- |
| `@wsrpc/server` | Node.js 22+ RPC servers with HTTP, Express or Fastify |
| `@wsrpc/client` | The existing browser client and typed Node.js client |

The original browser API is preserved. Servers, Node clients and reusable route
classes use ESM with TypeScript declarations. Both npm packages are released
from the same GitHub Release in [wsrpc-ts](https://github.com/wsrpc/wsrpc-ts).

```{toctree}
:maxdepth: 2

quick-start
client
../typescript/index
```

Python servers and clients have their own [Python guide](../python/index.md).
They remain compatible over the shared [protocol](../protocol.md).
