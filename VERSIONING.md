# Versioning Law

## Why versioning is important

Every normative artifact in this programme carries a version, and versions
only move forward. This is not bureaucracy. It is how a system that demands
to be trusted stays inspectable.

**Version numbers are decisions, not labels.** The glossary was v0.1.0 while
it was a draft — a proposal. It became v1.0.0 the moment HgX ratified it. The
number changed because the *status* changed. Anyone reading v0.1.0 knows: this
is not yet law. Anyone reading v1.0.0 knows: this is ratified. Without the
version, draft and law are indistinguishable — and a system that cannot
distinguish them cannot be trusted.

**Proofs check a specific version.** TLC found six genuine bugs in the state
machine. Each fix changed the spec. The proof report (3,266,929 states, zero
violations) is true *of the fixed spec* — not of the spec as first written.
Without versions, "the spec was proven" is a meaningless sentence: *which*
spec? Versioning binds every claim of correctness to the exact artifact it
was checked against.

**History must survive.** Papers I–III were rewritten (v1.1 → v1.2,
v1.0 → v1.1) while the old versions stand as historical record. HgX's
decision: the papers stand; the glossary governs. Versions let the old and
the new coexist honestly — growth on record, nothing silently replaced.

**The chronicle is the product.** The CHANGELOG, the commit history, the
build log — a year from now, this is how anyone (including us) reconstructs
what happened, when, and why. An unversioned project has no memory; a
versioned one can be audited.

## The law

1. Every normative artifact carries a version (SemVer): MAJOR.MINOR.PATCH.
2. v0.x.x = draft — proposed, not ratified. v1.0.0 = ratified by HgX —
   normative.
3. Versions only move forward. Never rewrite history; never silently replace.
4. Every version change is committed with a reason — the commit message says
   what changed and why.
5. Every proof, report, or claim of correctness names the exact version it
   was checked against.
6. The CHANGELOG is updated with every release. The build log records every
   release with date, time, and comment.

*Ratified as law by HgX's order, 2026-10-19.*
