# MCP sidecar template

A [Model Context Protocol](https://modelcontextprotocol.io/) server that
exposes one app's data or actions to AI agents (Open WebUI's native tool
support, or any other MCP-compatible client) — built and proven once,
for Nextcloud (`gentian-apps/images/nextcloud-mcp/`). This template is
that implementation with the Nextcloud-specific parts (WebDAV/XML
handling, `occ` commands, the actual tool logic) stripped out and
replaced with a minimal working example plus TODOs.

## What's in this directory

```
server.py          The MCP server itself (FastMCP, streamable-http transport)
requirements.txt    mcp + httpx — add more only if your tools need them
Dockerfile          Bakes requirements.txt in at build time (see root README
                     "Internet egress" — this is not optional)
chart/               Minimal Helm chart: one Deployment, no Service (see
                     root README — AppProfile.spec.sidecars.stableServiceName
                     handles that generically)
```

## Quick start

1. Copy this directory to `gentian-apps/images/<app>-mcp/`.
2. In `server.py`: rename `SIDECAR_NAME`, replace `UPSTREAM_BASE_URL`'s
   default and the auth env vars with what your app actually needs,
   delete the `ping` example and write your real `@mcp.tool()`
   functions.
3. In `chart/Chart.yaml`: rename `name` (and update `chart/values.yaml`'s
   `image.repository` / `upstreamBaseUrl` to match).
4. In `chart/templates/deployment.yaml`: add whatever env vars your new
   tools need (there's a TODO block showing the pattern).
5. Test locally (see "Testing" below) **before** wiring CI or a profile
   — every real bug in the Nextcloud sidecar was caught this way, not
   by reading the code.
6. Follow the root README's "Using a template" steps 3–4 (CI, profile
   wiring).

## Why FastMCP + streamable-http

`mcp.server.fastmcp.FastMCP` is the official Python SDK's high-level
API — `@mcp.tool()` turns a plain function (with a docstring, which
becomes the tool description the model sees) into an MCP tool with
almost no boilerplate. `streamable-http` is the modern HTTP transport
(replacing the older SSE transport) — the right choice for a sidecar
reached over a Kubernetes Service rather than spawned as a subprocess.

**`host="0.0.0.0"` in the `FastMCP(...)` constructor is required, not
optional.** It defaults to `127.0.0.1`, which is unreachable from
anything outside the container — including another container in the
*same* pod. This is the single most likely reason a freshly-templated
sidecar will be unreachable despite the pod showing `Running`.

## Tool design

- **Keep tools narrow.** `listX`/`searchX`/`readX` over an app's own
  read API, not broad write/delete/admin operations, unless the
  sidecar's whole purpose requires them. The account it authenticates
  as should physically be incapable of more than its tools expose (see
  root README "Authentication").
- **Docstrings are the tool description the model sees** — FastMCP
  extracts them directly. Write them for the model's benefit (what does
  this tool do, what do the parameters mean, what does it return), not
  as internal code comments.
- **URL-encode path segments explicitly** if any tool takes a
  user/model-supplied path or filename and you're building request URLs
  yourself — see the `GOTCHA` comment block in `server.py`. A raw
  f-string interpolation will silently mishandle `#`, and names read
  back from some upstream APIs (WebDAV in particular) come back
  percent-encoded and need `unquote()`-ing before you return them to
  the model.
- **Cap unbounded results.** Anything list-like (search results,
  directory listings) should have a hard max — an agent asking a vague
  question shouldn't be able to trigger a multi-megabyte tool response.

## Testing

Don't trust this until you've done all three:

1. **Call the tool functions directly** (`python3 -c "import server;
   print(server.myTool(...))"`) against a real, running instance of the
   app you're wrapping — not a mock of its API. Catches logic bugs fast.
2. **Run the actual server and connect a real MCP client** — the
   `mcp` package includes one:
   ```python
   import asyncio
   from mcp import ClientSession
   from mcp.client.streamable_http import streamablehttp_client

   async def main():
       async with streamablehttp_client("http://localhost:8765/mcp") as (r, w, _):
           async with ClientSession(r, w) as session:
               await session.initialize()
               print(await session.list_tools())
               print(await session.call_tool("myTool", {"arg": "value"}))

   asyncio.run(main())
   ```
   This is the only way to catch transport/protocol-level bugs — calling
   your Python functions directly skips FastMCP's own request/response
   handling entirely.
3. **Build the actual image and run it on the same Docker network as a
   real instance of the app**, not `localhost` — this is what caught the
   Nextcloud `trustedDomains` bug (worked fine against `localhost`,
   400'd against the container's real hostname, which is the topology
   that actually matters once deployed).

## Reference implementation

`gentian-apps/images/nextcloud-mcp/` — the real, deployed sidecar this
template was extracted from. Read it alongside this template if
anything here is unclear; it's the concrete answer to "what does a
filled-in version of this actually look like."
