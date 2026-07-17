# Git-modules sync sidecar template

A polling sidecar that clones a git repo and keeps a local checkout in sync on an interval —
for apps that load "modules"/plugins/config from a directory and need that directory kept
up to date from a git remote without rebuilding the app's own image.

## What's in this directory

```
sync.sh              The sync loop: initial clone, then periodic fetch+reset on SYNC_INTERVAL
Dockerfile            Bakes git + shell deps in at build time
chart/                Minimal Helm chart: Deployment, ConfigMap (post-sync hook script), PVC
                       (persistence.enabled — shared volume mounted into the primary app too)
```

Key env vars (see `chart/values.yaml` `git.*`, `syncDir`, `postSyncScript`):

| Variable | Purpose |
|---|---|
| `GIT_REPO_URL` | Repo to clone (required) |
| `GIT_BRANCH` | Branch to track (default `main`) |
| `SYNC_DIR` | Target checkout directory, shared via volume with the primary app |
| `SYNC_INTERVAL` | Seconds between fetch/reset cycles |

## Quick start

1. Copy this directory to `gentian-apps/images/<app>-git-modules/`.
2. Set `git.repoUrl`/`git.branch` in `chart/values.yaml`, and mount the same volume
   (`persistence.enabled` PVC or an `emptyDir`) into the primary app's container at the path
   it expects modules/plugins to live.
3. If the repo is private, wire `git.sshKey` (or switch `sync.sh` to a token-based HTTPS URL)
   as a sidecar-scoped secret — never bake credentials into the image (see root README
   "Authentication").
4. Test the sync loop against a real repo before wiring CI or an `AppProfile` — confirm the
   primary app actually picks up changes from the shared volume, not just that the clone
   succeeds.
5. Follow the root README's "Using a template" steps 3–4 (CI, profile wiring).

## Status

Early extraction, not yet validated against a second app — treat as a starting point. No
resource limits testing has been done for large repos; watch `SYNC_DIR` disk usage if the
target repo is large or grows unbounded.
