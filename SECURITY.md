# Security Policy

## The estate's posture

This repository is the public, sanitized record of the J.A.R.V.I.S. estate.
By doctrine:

- **No private material is ever published here.** No credentials, no personal
  data, no family or financial information. The publication boundary is
  absolute; anything private found here is a defect — please report it.
- **Credentials live in secure storage only.** Nothing in this repository
  requires, contains, or accepts a secret. Never open an issue containing
  one.
- **Human authority at every consequential boundary.** The system this repo
  documents sends, spends, publishes, and deletes nothing without the
  operator's explicit approval. Reports that describe bypassing that
  boundary are treated as security issues.
- **Formal security work.** Phase 5 (security boundaries) is closed.
  Phase 6 (router optimality) is open. Findings from readers are welcome.
- **Local Jarvis**, live in [`local-jarvis/`](local-jarvis/README.md) since
  2026-10-27, ships placeholders only (`CHANGE_ME`, `<user>`). Voice
  profiles, recordings, and weights stay on the machine. The voice path,
  VLC, and Ollama bind to localhost. The orchestrator listens on port 8080
  only after it is started. The voice loop is not auto-started.

## Supported versions

Only the latest state of `main` is supported. The estate versions forward
only (see [VERSIONING.md](VERSIONING.md)); fixes are never back-ported to
superseded versions, which are kept for the record.

## Reporting a vulnerability

Email **HgXengineering@gmail.com** (HgX, the operator) with the subject line
`SECURITY: jarvis-estate`. Please include:

- what you found and where (file, path, or URL),
- the impact you believe it has,
- steps to reproduce, if applicable.

Please do not open a public issue for a vulnerability, and do not disclose
it publicly until we have had a reasonable opportunity to respond. We aim to
acknowledge reports within three business days. Good-faith reports are
welcome and credited in the release log when a fix lands.
