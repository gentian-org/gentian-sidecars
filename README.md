# gentian-sidecars

Templates for building **sidecars** — small companion services deployed
alongside a Gentian OS app, using `AppProfile.spec.sidecars`. This repo
holds *templates* (shape, boilerplate, hard-won gotchas) — not
implementations. A real, deployed sidecar built from a template here
lives in `gentian-apps` (e.g. `images/nextcloud-mcp/`), alongside the
`AppProfile` that declares it.

## What a sidecar is, in this platform

`AppProfile.spec.sidecars` (gentian-os,
[`api/v1alpha1/appprofile_types.go`](https://github.com/gentian-org/gentian-os/blob/develop/api/v1alpha1/appprofile_types.go),
`AppSidecarSpec`) declares a companion service that gets deployed as its
**own Helm Release**, in the same tenant namespace as the primary app,
by the generic `app-default` Crossplane composition — no bespoke
`composition.yaml` needed. In outline, on the primary app's
`AppProfile`:

```yaml
spec:
  sidecars:
    - name: mcp                      # -> synthetic app key "{profile}-mcp"
      chart:
        repository: oci://ghcr.io/gentian-org/charts
        name: my-app-mcp
        version: "0.1.0"
      appSecrets:                    # sidecar-scoped, own OpenBao path --
        - name: service_password     # see "Authentication" below
          valuePath: someChartValueKey
      extraValues:
        image:
          repository: ghcr.io/gentian-org/my-app-mcp
          tag: "0.1.0"
      stableServiceName: my-app-mcp  # fixed Service name other pods can reach
      stableServicePort: 8765
```

Each sidecar gets:

- Its own Helm Release (`{xrName}-{sidecar}-release`), rendered from
  `chart` + `extraValues`, in the same namespace as the primary app.
- Its own `appSecrets`, synced from OpenBao at
  `gentian-os/tenants/<tenant>/apps/<parent>-<sidecar>/internal/<name>`
  (the `SidecarAppName` convention) into a Secret named
  `<parent>-<sidecar>-sensitive-values`, resolved server-side by
  Crossplane into a plain Helm `--set` value (never a live
  `secretKeyRef` the chart re-reads itself).
- An optional stable Service alias (`stableServiceName`/
  `stableServicePort`) selecting the sidecar's own pods by
  `app.kubernetes.io/instance` — the mechanism other same-namespace
  workloads (the primary app itself, or another sidecar) use to reach
  it by a fixed name.

**Not yet supported:** a sidecar's own `KernelRequirements` beyond OIDC
(database, cache, S3 for the sidecar itself) — the field exists on
`AppSidecarSpec` but isn't wired into the sidecar's own Release values
yet. If your sidecar needs its own database, that's real gentian-os work
first, not something a template can paper over.

See `gentian-apps/app-profile-guide.md` §13 ("Post-install bootstrap
jobs") for the sibling `postInstallJob` mechanism, and the profile
placement decision table there for when to reach for a sidecar vs. a
`postInstallJob` vs. a full custom `composition.yaml`.

## Repo structure

```
templates/
  mcp/       Model Context Protocol servers — expose an app's data/actions
             to AI agents (Open WebUI's native tool support, etc.)
  sso/       Auth/session bridges — not yet extracted into a template,
             see templates/sso/README.md for the closest existing reference
  webhook/   Event-driven push sidecars (e.g. backing AppProfile's
             automationHooks) — not yet extracted, see
             templates/webhook/README.md
```

Pick the folder matching what your sidecar *does*, not what app it's
for — the category is about the sidecar's role (agent-facing tool
server, auth bridge, event pusher), not the upstream app.

**Templates are extracted from real, deployed sidecars, not designed
ahead of one.** `templates/mcp/` exists because `nextcloud-mcp` was
built and deployed first — see its README for what's proven-generic
vs. what's still a single data point. `sso/` and `webhook/` are
placeholders until there's a first real instance to generalize from;
resist the urge to fill them in speculatively.

## Using a template

1. Copy the whole category folder into `gentian-apps/images/<app>-<category>/`
   (e.g. `images/openproject-mcp/`).
2. Follow the `README.md` inside that folder — each one has its own
   walkthrough, since the details (auth pattern, transport, chart
   quirks) differ meaningfully by category.
3. Wire CI: add a build job to `gentian-apps/.github/workflows/apps-ci.yaml`
   following the existing `build-nextcloud-mcp` job as a pattern (builds
   + pushes both the image and the Helm chart to `oci://ghcr.io/gentian-org/charts`).
4. Declare it on the app's `AppProfile` (`spec.sidecars`, see above) and
   add whatever `postInstallJob`/hook provisions the credentials it
   authenticates with (see "Authentication" below).

## Cross-cutting patterns

These apply regardless of category — learned building `nextcloud-mcp`,
the first real instance.

### Internet egress

The tenant namespace's NetworkPolicy blocks general internet egress by
default. A sidecar that tries to `pip install`/`apk add`/`npm install`
at container **startup** will hang until it exhausts its retries —
observed first-hand as a stuck Job, ~2 minutes per failed attempt, no
useful error in the logs. **Bake every dependency into the image at
build time.** Runtime network access is fine for calls to the app
itself (same namespace) or anything explicitly allow-listed via
`gentianos.io/kernel-egress-namespaces` — never for pulling packages.

### Authentication

Authenticate as a **dedicated, low-privilege account** — never the
app's admin account, and never the identity of whichever user happens
to be chatting with the model. Concretely (the pattern `nextcloud-mcp`
uses, reusable across categories):

1. Give the sidecar its own `appSecrets` entry (sidecar-scoped OpenBao
   path, see above) holding a generated password/token.
2. Have the **primary app** provision the matching account, reading that
   *same* secret — for a Helm-hooks-capable chart, mount the sidecar's
   Secret (`<parent>-<sidecar>-sensitive-values`, a fully deterministic
   name once you know the sidecar's own name) into the primary app's pod
   as a second volume, and read it from a `post-installation`-style
   hook. For an app without hooks, use a `postInstallJob` instead (see
   the gentian-apps guide). Either way: **the account gets provisioned
   from the sidecar's own secret, not a newly-generated one** — both
   sides must read the exact same value, or auth fails.
3. Never widen the account's access beyond what the sidecar's tools
   actually need. `nextcloud-mcp`'s account only ever sees its own
   Nextcloud file space — nothing shared, nothing admin-scoped.

### Reaching the app over its in-namespace Service name

If your app's chart validates the `Host` header on incoming requests
(Nextcloud does, via `trustedDomains`) — and many do — the sidecar's
same-namespace calls (`http://myapp`) will be **rejected** unless that
short name is explicitly trusted. The app usually only auto-trusts its
public ingress hostname by default. Check for an equivalent
allow-list setting in your app's chart before assuming same-namespace
calls will just work; this is *not* an MCP-specific or Nextcloud-specific
quirk, most self-hosted apps that care about Host-header spoofing have
some version of it.

### Verify against the real app, not a mock

Every non-trivial bug found building `nextcloud-mcp` — percent-encoded
filenames, a `#` silently truncating a request, the trusted-domains
400 — only surfaced when testing against an actual running instance of
the app (a local Docker container is enough) through the real client
protocol, not by calling the sidecar's own functions directly or
mocking the upstream API. Mocking the app you're wrapping risks baking
your own misunderstanding of its API into both the mock and the
implementation, so nothing ever catches the mismatch.
