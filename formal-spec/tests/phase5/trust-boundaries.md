# Phase 5 — Trust Boundary Map

**Status:** v0.1-draft · **Date:** 2026-10-22
**Sources:** `ROADMAP.md` §8 (the ten boundaries); `tests/PHASE-5-PLAN.md`
(custody doctrines, head-start note); `tests/PHASE-5-OPEN-QUESTIONS.md` Q3, Q6
(answered 2026-10-22); `asset-register.md` (AR-1…AR-15).

> **Governance.** Draft until HgX ratifies. The custody doctrines are
> formalized as named boundaries, described exactly as ordered, never
> redesigned (Q6). **The live-location custodian is never named outside
> its own chat** — boundary TB-14 names the boundary and its crossing
> rules only. Where description would weaken a control, the control
> wins: the boundary is named, never the custodian.

---

## 1. Purpose

A trust boundary is a line across which a subject's authority changes.
This map draws the estate's lines: the roadmap's ten, plus the lived
custody doctrines as named boundaries (Q6). Every entry names the
subjects on each side, the assets in play, and the crossing rules.

## 2. The roadmap's ten boundaries

| ID | Boundary | Subjects | Assets | Crossing rules |
|---|---|---|---|---|
| TB-1 | HgX devices ↔ estate edge | HgX + enrolled devices ↔ edge services | AR-2, AR-9 | Only enrolled sessions cross (`session-lifecycle.md`); unknown sessions refused before any other check; approval authority never leaves HgX. |
| TB-2 | Estate edge ↔ orchestrator | Edge services ↔ orchestrator | AR-2, AR-11 | Intent digest + session + expiry validated at the edge; the orchestrator re-validates before consequence. |
| TB-3 | Orchestrator ↔ tools | Orchestrator ↔ tool plane | AR-10, AR-11, AR-12 | Tool output is verification input, never instruction; false outcome reporting is a named Tampering threat (T-8). |
| TB-4 | Orchestrator ↔ subagents | Orchestrator ↔ subagents | AR-11 | Subagent output is verification input; no proof, no done; the orchestrator is accountable for every handoff. |
| TB-5 | Orchestrator ↔ connectors | Orchestrator ↔ external integrations | AR-13, AR-6, AR-7, AR-8 | Connector least privilege; finance and communications integrations route through custody boundaries TB-11/TB-12. |
| TB-6 | Orchestrator ↔ external web | Orchestrator ↔ fetched content | — | External content is untrusted data, never instructions (prompt-injection discipline, T-22). |
| TB-7 | Orchestrator ↔ Secure Vault | Orchestrator ↔ credential store | AR-3, AR-9 | No component outside the vault holds key bytes; no credential in prompt context; no raw secret in evidence. |
| TB-8 | Orchestrator ↔ external router | Orchestrator ↔ usage router | AR-14, AR-15 | The router recommends a path only; it never approves, authorizes spending, or becomes a second orchestrator. |
| TB-9 | Client ↔ notification system | Clients ↔ notification delivery | AR-1 | Notifications are hints, not authoritative state; no payload beyond pointer + state; silent-by-default. |
| TB-10 | Personal surfaces ↔ shared surfaces | HgX's private views ↔ shared/screen contexts | AR-6, AR-7, AR-8 | Shared screens show states only; restricted content never renders on shared surfaces (INV-S5). |

## 3. The custody doctrines as named boundaries (Q6)

| ID | Boundary | Subjects | Assets | Crossing rules |
|---|---|---|---|---|
| TB-11 | Money-access custody boundary | Sole money custodian ↔ any other room | AR-5 | One custodian holds all money access; any money need elsewhere routes to HgX personally, one approval = one exact amount, account, date; nothing silent. |
| TB-12 | Calendar-communications-tasks custody boundary | Sole calendar/email/tasks custodian ↔ any other room | AR-6, AR-7 | One custodian holds all calendar, email, and task access estate-wide; no other bot, chat, worker, or system reads, manages, or speaks for them. |
| TB-13 | Health-data sealed boundary | Health service ↔ everything else | AR-4 | Sealed: health contents never cross any boundary — never to another chat, summary, oversight report, or the estate's other services. No location used inside. |
| TB-14 | Live-location custody boundary | Sole live-location custodian ↔ everything else | (governed, not enumerated) | The boundary is named; **the custodian is never named outside its own chat**. No other bot, chat, worker, or system reads, requests, stores, or uses live location; every location-dependent need routes to HgX personally. |
| TB-15 | Research-lab sealed boundary | R&D lab ↔ working room and estate | research outputs | Sealed: findings cross no boundary back — not to the working room, not to any bot, chat, worker, or system. Publication routes only on HgX's explicit command for that item, and never through the working room. |

## 4. Trust-boundary diagram (ASCII)

```text
                      ┌──────────┐
                      │   HgX    │  (sole holder of approval authority, AR-2)
                      └────┬─────┘
                           │ TB-1  enrolled sessions only
                    ┌───────┴────────┐
                    │  ESTATE EDGE   │
                    └───────┬────────┘
                            │ TB-2  digest + session + expiry validated
               ┌────────────┴────────────┐
               │      ORCHESTRATOR       │
               └─┬───┬───┬───┬───┬───┬───┘
        TB-3      │   │TB-4 │   │TB-5 │   │TB-6      TB-7      TB-8
     (tools)      │   │     │   │     │  (web)   (vault)   (router)
          ┌───────┘   │  ┌──┴──┐│ ┌───┴────┐
          │ tools     │  │sub- ││ │connect-│
          │ (verify   │  │agents││ │ors     │
          │  input)   │  │no   ││ │least   │
          │           │  │proof││ │priv.   │
          └───────────┘  │no   ││ └───┬────┘
                         │done ││     │
                         └─────┘│ TB-11 (money custody)   TB-12 (calendar/email/tasks)
                                │ TB-13 (health sealed)   TB-14 (live-location custody)
                                │ TB-15 (research sealed)
  TB-9: clients → notifications are hints, never state
  TB-10: personal surfaces ↔ shared surfaces — states only, never restricted content
```

## 5. Numbered claims

- **TB-1.** The roadmap's ten boundaries (TB-1…TB-10) are adopted
  verbatim as the model's structural boundaries.
- **TB-2.** The five custody doctrines (TB-11…TB-15) are adopted as
  named trust boundaries with subjects, assets, and crossing rules
  (Q6).
- **TB-3.** The doctrines are described exactly as ordered, never
  redesigned; nothing in this map changes who holds what.
- **TB-4.** The live-location custodian is never named in this map or
  anywhere outside its own chat; TB-14 names the boundary and its
  crossing rules only — where description would weaken the secrecy
  control, the control wins (Q6).
- **TB-5.** Sealed means sealed: TB-13 (health) and TB-15 (research)
  permit no content crossing in the model's normal operation;
  TB-15's only exit is HgX's explicit per-item command, never
  through the working room.
- **TB-6.** At L0 (procedural, Q3) these boundaries are enforced by
  doctrine, roster discipline, and HgX's word — not by mechanism.
  The compensations for what L0 cannot enforce are in
  `control-matrix.md` §5 and the upgrade path in
  `isolation-upgrade-roadmap.md`.

## 6. Open points

- **P5-OP-1 — Custodian bot roster.** The map names the custodians
  Money Bot and Tickler Bot because HgX's custody orders name them;
  other named role-bots (News, Food, Tax, Family, Fantasy) have no
  custody and are not mapped. Whether each role-bot's authority
  should be a matrix row is deferred to HgX. **Needs HgX's word** if
  the matrix is to enumerate them. **RESOLVED 2026-10-22 ~13:26 ET: enumerate every role-bot — each role-bot's authority becomes a matrix row (custody or none).**
- **P5-OP-2 — TB-2 edge re-validation.** The edge validates intent
  digest + session + expiry and the orchestrator re-validates before
  consequence; whether a third validation belongs at the tool plane
  (TB-3) is implementation depth. **Needs HgX's word** only if he
  wants the belt-and-braces depth specified here. **RESOLVED 2026-10-22 ~13:27 ET: specify the third validation at the tool plane (TB-3).**

## 7. Cross-references

- `asset-register.md` — AR-1…AR-15 placed against these boundaries.
- `capability-matrix.md` — the eight-field vocabulary applied at each
  boundary.
- `threat-catalogue.md` — every threat names the boundary it crosses.
- `session-lifecycle.md` — TB-1's session foundation, specified in
  full (Q1).
- `control-matrix.md` — the L0 compensations (§5).
- `isolation-upgrade-roadmap.md` — what each level would enforce.

## 8. Version history

- **v0.1-draft — 2026-10-22.** First draft: TB-1…TB-15 mapped with
  subjects, assets, crossing rules; ASCII diagram; Q6 baked in;
  P5-OP-1, P5-OP-2 recorded. Not ratified.
