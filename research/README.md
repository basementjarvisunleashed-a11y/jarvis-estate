# Research — layout convention

The estate's published research, filed by day. HgX adds research daily; this
tree is built to receive it without redesign.

## Layout

```
research/
  README.md                      ← this file: the convention
  YYYY-MM-DD/                    ← one folder per day, date in America/Toronto
    <slug>.md                    ← canonical source (faithful to the research desk)
    <slug>.html                  ← entry page: full report, hub-styled
```

- One dated folder per day: `research/2026-10-21/`, `research/2026-10-22/`, …
- The slug is the kebab-case short title: `bitcoin-vbyte-fee-stats`,
  `hashrate-per-halving-vs-price`, …
- The `.md` is the canonical source — published as written, never rewritten.
- The `.html` is the entry page — full report text, hub dark styling, with a
  "back to research index" link (`../../index.html#research`) and a link to
  the source markdown.
- URL scheme (GitHub Pages): `research/2026-10-21/<slug>.html`

## Adding a new day's research (repeatable template)

1. Research Bot drops the scrubbed markdown into Dropbox
   `/J.A.R.V.I.S./research/<date>/` and hands the release office the file.
2. Release office copies it verbatim to `research/<date>/<slug>.md`.
3. Release office builds `research/<date>/<slug>.html` from the entry-page
   template (copy the previous day's page; swap title, date, body; keep the
   header/footer chrome and the back link).
4. Release office prepends one entry to the hub's Research index
   (`index.html` + `website/index.html`, section `#research`): date, title,
   one-line summary, link to `research/<date>/<slug>.html`.
5. Commit, push, verify live. The index is reverse-chronological —
   newest entry first — so it extends cleanly every day.

## Entry template (hub index)

```html
<li class="research-entry">
  <div class="research-meta"><time datetime="YYYY-MM-DD">YYYY-MM-DD</time></div>
  <h3><a href="research/YYYY-MM-DD/&lt;slug&gt;.html">Title</a></h3>
  <p class="research-summary">One-line summary.</p>
</li>
```

## Entry template (entry page)

Copy `research/2026-10-21/bitcoin-vbyte-fee-stats.html`. Keep: the `<style>`
block, topbar, kicker/date line, scrub-statement box, footer. Replace: the
`<title>`, `<h1>`, meta lines, and the full report body (faithful to source —
tables as tables, lists as lists, links intact).
