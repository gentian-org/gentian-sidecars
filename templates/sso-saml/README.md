# SSO SAML sidecar template

A minimal SAML 2.0 login bridge — generates the `AuthnRequest` redirect, receives the
Assertion Consumer Service (ACS) callback, and hands the parsed profile to a pluggable
per-app handler script. Use this for apps that speak SAML but need a small bridge in front
of them to talk to the kernel's identity provider.

## What's in this directory

```
bridge.js           The bridge server (plain Node http, no framework); loads a pluggable
                     handler.js at APP_HANDLER_SCRIPT and calls its onLogin(profile, req, res)
Dockerfile           Bakes npm deps (pg, mysql2, jsonwebtoken) in at build time
chart/               Minimal Helm chart: Deployment, Service, ConfigMap. The ConfigMap
                     renders chart/values.yaml's `handlerScript` into handler.js at
                     APP_HANDLER_SCRIPT — that's where the per-app login logic lives,
                     not a file in this directory.
```

## Quick start

1. Copy this directory to `gentian-apps/images/<app>-sso-saml/`.
2. Set `sso.tenantId`, `sso.kernelDomain`, `sso.issuer` in `chart/values.yaml` for the target
   app.
3. Write the app-specific `handlerScript` in `chart/values.yaml` — this is what actually
   provisions/logs in the user in the wrapped app once SAML validates.
4. Test the SAML redirect + ACS callback against a real IdP-backed login before wiring CI or
   an `AppProfile` (see root README "Verify against the real app, not a mock").
5. Follow the root README's "Using a template" steps 3–4 (CI, profile wiring).

## Status

This is an early extraction, not yet validated against a second app beyond the one it was
built for — treat `bridge.js` as a starting point, not a finished bridge. Cross-check against
the root README's "Reaching the app over its in-namespace Service name" note if the wrapped
app validates the `Host` header.
