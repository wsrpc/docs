# JavaScript / TypeScript quick start

Expose `echo` and a reverse `callback` at `ws://127.0.0.1:8000/ws/`.
The complete examples use Node.js 24+ to run `.ts` directly; the compiled
library supports Node.js 22+.

## Install

Choose a framework. The install and server tabs stay in sync.
Before the first npm release, use the [local package archives](../typescript/index.md#install-from-a-checkout).

`````{tab-set}
:sync-group: js-framework

````{tab-item} Node HTTP
:sync: node

```shell
npm install @wsrpc/server @wsrpc/client
```
````

````{tab-item} Express
:sync: express

```shell
npm install @wsrpc/server @wsrpc/client express
```
````

````{tab-item} Fastify
:sync: fastify

```shell
npm install @wsrpc/server @wsrpc/client fastify
```
````

`````

## Start the server

Save the selected complete example as `app.ts`. Each handles ordinary HTTP
`GET /health`, registers its RPC methods and closes connections on shutdown.

`````{tab-set}
:sync-group: js-framework

````{tab-item} Node HTTP
:sync: node

```{literalinclude} ../typescript/examples/http.ts
:language: typescript
```

```shell
node app.ts
```
````

````{tab-item} Express
:sync: express

```{literalinclude} ../typescript/examples/express.ts
:language: typescript
```

```shell
node app.ts
```
````

````{tab-item} Fastify
:sync: fastify

```{literalinclude} ../typescript/examples/fastify.ts
:language: typescript
```

```shell
node app.ts
```
````

`````

## Connect a Node client

Save as `client.ts` and run `node client.ts` in another terminal:

```{literalinclude} ../typescript/examples/client.ts
:language: typescript
```

It prints `{ message: 'Hello' }` and `42`. The callback route is registered
before connecting, so the server can call the client immediately. The
`finally` block closes the connection.

For a frontend, use the [browser client](client.md#browser). Continue with
[typed contracts, route classes and implicit context](../typescript/index.md).
The [Python clients](../python/clients.md) can call this server too.
