# Website

GitHub Pages publishes the **repository root** (`/`) on `main`. The live
homepage is [`/index.html`](../index.html):

https://basementjarvisunleashed-a11y.github.io/jarvis-estate/

That page is the current site as of 2026-10-27: Local Jarvis, architecture,
download, docs, research, and the build chronicle. It is static. It loads
no tracking scripts and no third-party fonts.

## Archived hub — deprecated for publishing

[`index.html`](index.html) in this directory is the previous white-paper
hub (the full in-browser readers). It is **deprecated** as a homepage.
Keep it: it is the readable copy of Papers I–III. Do not replace the root
homepage with this file.

Relative links inside this copy point one directory up (`../academy/…`)
so they resolve when the file is opened from `website/`. A banner at the
top of the page says the same thing.

Dropbox buttons on the archived hub currently ask for a Dropbox login
(checked 2026-10-27). The URLs were not replaced.

## Updates

Edit the root `index.html` for the public site. Append build-log objects
at the **start** of the `buildlog-data` JSON (newest first) so
`.github/workflows/validate.yml` still parses a non-empty array. Research
entry pages link to `index.html#research` at the repository root; keep
that anchor.
