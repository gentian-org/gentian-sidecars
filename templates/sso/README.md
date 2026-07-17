# SSO / auth-bridge sidecars — not yet templated

No template lives here yet. Per the root README: templates get
extracted from a real, deployed sidecar, not designed ahead of one —
and there isn't yet a sidecar in this category built on
`AppProfile.spec.sidecars`.

## Closest existing reference

`gentian-apps/profiles/openproject/composition.yaml`'s "portal-bridge"
sidecar (search that file for `portal-bridge`) is shaped like what
would go here — a small companion service translating the portal
shell's session into a ticket/form-login flow OpenProject itself
understands, deployed alongside the primary app. **It predates
`spec.sidecars`** and is implemented as a bespoke inline
ConfigMap+Deployment+Service inside OpenProject's own
custom `composition.yaml`, not the generic mechanism — read it for the
*problem shape*, not as a pattern to copy mechanically.

## When to build this template

Once a second SSO/auth-bridge sidecar exists (built on
`spec.sidecars`, ideally with the portal-bridge migrated to match), the
actual shared shape between the two becomes visible — extract the
template from what's genuinely common between them, not from guessing
in advance what "an SSO sidecar" looks like in general. See the root
README's `templates/mcp/` for how that played out for MCP servers: the
boilerplate that survived contact with a real implementation (Dockerfile
shape, chart skeleton, the dedicated-account auth pattern) turned out
to be a small fraction of the total code — most of it was genuinely
app-specific and wouldn't have been the same for a second instance.
