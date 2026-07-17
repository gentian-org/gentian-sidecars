# MCP server sidecar template -- see README.md in this directory.
#
# Sidecars run in the tenant namespace, whose NetworkPolicy blocks general
# internet egress by default -- dependencies MUST be baked in at build
# time (this Dockerfile). A runtime `pip install`/`apk add` will hang
# until the container's retries are exhausted; see README.md "Internet
# egress" for how this was discovered.
FROM python:3.12-alpine

RUN adduser -D -u 1000 mcp
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

USER mcp
EXPOSE 8765

LABEL org.opencontainers.image.title="CHANGEME MCP Sidecar" \
      org.opencontainers.image.description="TODO: describe what this sidecar exposes to AI agents"

CMD ["python3", "server.py"]
