# STAGING — contracts/README.md v1.1 — APPLIED 2026-10-20 23:58 ET on HgX's word ("let's fix all the bugs").
Proposed version action for finding D-C. HgX gave the word; original now carries the fix as ratified v1.1.
Per VERSIONING.md: v1.0.0 ratified → v1.1-draft proposed change → ratified
v1.1 only on HgX's approval.

## Current line 18 (v1.0.0, sha256 e69e9a9ce4e1b315)
| `contracts/glossary.md` | The canonical glossary: 69 normative term definitions, 25 vocabulary conflicts with resolutions, 6 terms flagged unresolved. The single vocabulary the model checker, test suite, and doctoral committee refer to. | Phase 0 coordinator; **HgX ratifies (v1.0.0 gate)** |

## Proposed line 18 (v1.1-draft)
| `contracts/glossary.md` | The canonical glossary: 69 normative term definitions, 25 vocabulary conflicts with resolutions, 3 open questions (U-2, U-3, U-4); 3 resolved at ratification (U-1, U-5, U-6). The single vocabulary the model checker, test suite, and doctoral committee refer to. | Phase 0 coordinator; **HgX ratifies (v1.0.0 gate)** |

## Evidence for the change
contracts/glossary.md §3 lists 6 entries: U-1, U-5, U-6 carry
"RESOLVED 2026-10-19 (HgX)"; U-2 (revision token, owner Phase 3),
U-3 (freshness values, owner Phase 3), U-4 (safe-point semantics,
owner Phase 4) remain open. No other line changes proposed in this draft.

## Proposed CHANGELOG entry
- CONTRACTS: README.md v1.0.0 → v1.1-draft — unresolved-term count
  corrected ("6" → "3 open: U-2, U-3, U-4"), matching glossary §3's
  own 2026-10-19 ratification record.
