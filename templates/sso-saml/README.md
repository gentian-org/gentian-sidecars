# Sign-in sidecar — not a template

There is nothing to copy here, on purpose.

The sidecar that signs people in to an app which can do neither OIDC nor SAML is **one program,
run by the platform**, not something each app builds for itself:

- **The sidecar** is in gentian-apps, `images/gentian-sidecar-sso-saml/`. That is its only copy.
  Its README says what it accepts as the identity provider's answer, what a handler is given and
  what a handler may answer.
- **An app declares it** in its catalogue entry, `requires.services.identity.sidecar`, and brings
  one file, the handler: the code that makes a session in that app for the person the sidecar
  names. gentian-os, `docs/app-customization.md` ("The sign-in sidecar"), has the declaration and
  what the platform does for it; `docs/design/security.md` has what guards it.
- **Two worked handlers**: `profiles/docmost/docmost-ce/assets/sign-in-handler.js` and
  `profiles/activepieces/activepieces-me/assets/sign-in-handler.js` in gentian-apps, each with an
  end-to-end test against the real app.

## Why the copy that was here is gone

This directory held an early extraction of the sidecar: `bridge.js`, a Dockerfile and a chart. It
took whatever was posted to it at its word — it read an e-mail address out of the XML with a
pattern and checked no signature — and it was kept in step with nothing. A second copy of the
program that decides whether a sign-in is genuine is a copy that is wrong sooner or later, and a
template invites a third.

So: do not build a sign-in sidecar from a template. Write a handler for the platform's.
