# Webhook / event-push sidecars — not yet templated

No template lives here yet, and unlike `templates/sso/`, there isn't
even a bespoke reference implementation to point at — nothing in this
category has been built on this platform yet.

## Where this fits in the platform

`AppProfile.spec.automationHooks` (see
`gentian-os/docs/design/agentic-ai.md` §5, "Automation Hooks") is the
intended consumer: apps declare events they can emit
(`deliveryMode: webhook`) and actions workflow engines (ActivePieces,
future n8n) can trigger. A sidecar in this category would most likely
be the thing translating between an app's own event/webhook format and
whatever the platform's automation layer expects — but as of this
writing `automationHooks` itself is a schema-only field, same starting
state MCP was in before `nextcloud-mcp` was built (see the root repo's
`README.md`).

## When to build this template

Don't design this speculatively. Once there's a real reason to build
the first webhook-shaped sidecar — a specific app, a specific
automation need — build that one first, on `spec.sidecars`, verified
end-to-end against the real app the same way `nextcloud-mcp` was (see
root README "Verify against the real app, not a mock"). Extract the
template from what that instance actually needed, not from what seems
likely to generalize in advance.
