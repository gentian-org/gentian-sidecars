# AGENTS.md — gentian-sidecars

## Project overview

`gentian-sidecars` holds **templates** for building sidecars — companion services deployed
alongside a Gentian OS app via `AppProfile.spec.sidecars`. This repo has no live
implementations of its own; real, deployed sidecars built from these templates live in
[gentian-apps](https://github.com/gentian-org/gentian-apps) (e.g. `images/nextcloud-mcp/`).
See [README.md](README.md) for the sidecar mechanism, category layout, and cross-cutting
patterns (egress, auth, Host-header trust, testing against the real app).

## Build & deployment — none here

* This repo has no CI and nothing to deploy — it's a template library. "Using" a template
  means copying it into `gentian-apps/images/<app>-<category>/`, where that repo's own CI
  (`apps-ci.yaml`) builds and pushes it, and ArgoCD/the operator roll it out as part of the
  target app's `AppProfile`.
* Templates are extracted from real, deployed sidecars, not designed ahead of one (see
  README) — don't flesh out a placeholder template (`sso/`, `webhook/`) speculatively; wait
  for a first real instance to generalize from.

## Security & licensing

* **Never commit secrets** into a template — templates should only ever reference secrets by
  env var / OpenBao path convention, never contain real credentials, even as examples.
* **Respect third-party license terms** for any vendored library or snippet a template bakes
  into its Dockerfile.
