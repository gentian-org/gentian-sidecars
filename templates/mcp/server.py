"""MCP server sidecar template.

Copy this whole directory (e.g. to gentian-apps/images/<app>-mcp/), then:

  1. Rename SIDECAR_NAME below and in chart/Chart.yaml.
  2. Replace UPSTREAM_BASE_URL / the auth env vars with whatever your
     app's API actually needs (see README.md "Authentication").
  3. Replace the example `ping` tool with your app's real capabilities.
  4. Update requirements.txt if you need more than mcp + httpx.

See README.md in this directory for the full walkthrough, and
gentian-apps/images/nextcloud-mcp/ (in the gentian-apps repo) for a
complete, deployed example built from this exact template.
"""

import os

import httpx
from mcp.server.fastmcp import FastMCP

SIDECAR_NAME = "CHANGEME-mcp"  # TODO: rename, e.g. "openproject-mcp"

# TODO: replace with whatever your app needs to authenticate. The
# recommended pattern is a dedicated, low-privilege service account —
# never the app's admin account or the user currently chatting with the
# model. See README.md "Authentication" for how to provision one and
# share its credentials with this sidecar.
UPSTREAM_BASE_URL = os.environ.get("UPSTREAM_BASE_URL", "http://CHANGEME")

# host must be 0.0.0.0 -- FastMCP defaults to 127.0.0.1, which is
# unreachable from other pods/containers even when this sidecar runs in
# the same pod as the app it's exposing.
mcp = FastMCP(
    SIDECAR_NAME,
    host="0.0.0.0",
    port=int(os.environ.get("MCP_PORT", "8765")),
)


@mcp.tool()
def ping() -> str:
    """Example tool -- delete this and add your app's real capabilities.

    Keep tools narrow and read-mostly where possible: listX/searchX/readX
    rather than broad write/delete/admin operations, unless the sidecar
    genuinely needs write access to do its job. See README.md "Scope".
    """
    return f"{SIDECAR_NAME} is alive, configured to talk to {UPSTREAM_BASE_URL}"


# Example of calling out to the upstream app -- httpx is already a
# dependency (FastMCP's own streamable-http transport uses it). If your
# app's API is REST/JSON, this is usually all you need; delete if unused.
def _client() -> httpx.Client:
    return httpx.Client(timeout=15.0)  # TODO: add auth=(...) or headers={...}


# GOTCHA, hard-won building the Nextcloud MCP sidecar: if you construct
# request URLs by interpolating a path/filename directly into an f-string
# (f"{UPSTREAM_BASE_URL}/{path}"), a "#" anywhere in that path is treated
# as a URL fragment delimiter -- httpx silently drops everything after it
# without erroring, truncating the request. If your tool inputs can
# contain arbitrary user-controlled path segments (filenames, IDs with
# special characters), URL-encode each segment explicitly instead:
#
#   from urllib.parse import quote
#   def _url(path: str) -> str:
#       segments = [quote(seg, safe="") for seg in path.strip("/").split("/") if seg]
#       return UPSTREAM_BASE_URL + "/" + "/".join(segments)
#
# And if you read names back out of the upstream API's own response
# (e.g. a WebDAV href), remember those often come back percent-encoded
# too -- unquote() them before returning to the model, or it'll see
# "My%20File.txt" instead of "My File.txt".

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
