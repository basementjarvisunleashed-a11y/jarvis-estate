# Phase 5 — Attack Trees

**Status:** v0.1-draft · **Date:** 2026-10-22
**Sources:** `ROADMAP.md` §8 (threat model); `tests/PHASE-5-PLAN.md` (attack-tree
deliverable); `threat-catalogue.md` (T-1…T-28); `control-matrix.md` (control IDs);
`session-lifecycle.md` (Q1); `tests/phase4/ambiguity-protocol.md` (AP rules).

> **Governance.** Draft until HgX ratifies. Each tree works one highest-risk
> threat from goal to leaf; **every leaf names the control that stops it**.
> Leaf controls are IDs from `control-matrix.md`.

---

## 1. Purpose

The catalogue names the threats; the trees walk them. Four trees for
the highest-risk threats — fake approval, mutated intent,
prompt-injection egress, approval fatigue — each drawn to the leaf
where a named control stops the attacker. If a leaf cannot be stopped,
the tree must say so; none here are unstopped.

## 2. AT-1 — Fake approval (T-1)

Goal: execute a consequential action without HgX's real approval.

```text
fake-approval
├─ forge the approval object
│  ├─ invent an intent digest ................. stops at leaf: C-4 (digest binding — invented digest cannot match a live intent)
│  └─ replay a spent approval ................. stops at leaf: C-5 (single-use approval records — duplicate returns existing decision, never a second execution)
├─ impersonate the device
│  ├─ present an unenrolled device_session_id .. stops at leaf: C-1 (unknown sessions refused before any other check — session-lifecycle.md SL-3)
│  ├─ use a revoked session ................... stops at leaf: C-2 (revocation kills authority immediately — SL-14)
│  └─ use an expired session .................. stops at leaf: C-3 (expiry kills authority — SL-15)
└─ coerce the gesture
   ├─ render a misleading approval card ....... stops at leaf: C-6 (cards render exact target+effect+scope+expiry from the digest-bound intent; no adjacent content)
   └─ approve while offline, then reconnect ... stops at leaf: C-7 (offline taps are gestures, never consent — no authoritative approval without server validation)
```

## 3. AT-2 — Mutated intent (T-4)

Goal: get approval for a benign action, then execute a different one.

```text
mutated-intent
├─ mutate after approval
│  ├─ change the target ....................... stops at leaf: C-4 (approval binds target; changed target voids approval)
│  ├─ change the effect/scope ................. stops at leaf: C-4 (same binding — scope change voids approval)
│  └─ let the approval expire, execute late ... stops at leaf: C-8 (expiry evaluated at decision time; expired approvals unusable)
├─ mutate between card and server
│  └─ race a changed intent past the card ..... stops at leaf: C-9 (server re-validates intent digest + session + expiry at decision time — TB-2 crossing rule)
└─ mutate the evidence instead
   └─ alter the artifact after execution ....... stops at leaf: C-10 (artifact content digests; evidence references are revision-stable)
```

## 4. AT-3 — Prompt-injection egress (T-13/T-22)

Goal: get the estate to act on injected instructions or leak data outward.

```text
prompt-injection-egress
├─ inject via fetched web content
│  ├─ instructions in a page HgX asked about .... stops at leaf: C-11 (external content is untrusted data, never instructions — TB-6 crossing rule)
│  └─ fake "system" framing in page text ........ stops at leaf: C-11 (same discipline; provenance: content source is never the authority)
├─ inject via tool output
│  └─ a tool report carrying an instruction ...... stops at leaf: C-12 (tool output is verification input at TB-3; instructions require the approval path, not the data path)
├─ inject via subagent report
│  └─ a subagent report carrying an instruction .. stops at leaf: C-13 (subagent output is verification input at TB-4; the orchestrator does not execute instructions found in data)
└─ egress via a compromised path
   ├─ leak through notification payload ......... stops at leaf: C-14 (notification redaction — hints carry pointer+state only)
   ├─ leak via shared surface ................... stops at leaf: C-15 (states-only rendering — INV-S5)
   └─ leak via credentials in context ........... stops at leaf: C-16 (no credentials in prompt context; vault boundary TB-7)
```

## 5. AT-4 — Approval fatigue (T-24)

Goal: degrade HgX's approval judgment until a consequential action slips through.

```text
approval-fatigue
├─ flood with approval requests
│  ├─ barrage of low-risk approvals ............. stops at leaf: C-17 (silent-by-default + tiered escalation; routine approvals are not requested)
│  └─ bulk-approve pressure ("approve all") ..... stops at leaf: C-18 (no bulk approval — each intent is approved singly, exact target+effect)
├─ desensitize with lookalikes
│  ├─ a high-risk intent disguised as routine ... stops at leaf: C-19 (risk classes; high-risk requires local auth and exact target+effect rendering)
│  └─ drift the scope between renders ........... stops at leaf: C-4 (scope change voids approval — the card's digest is bound)
└─ exploit instrumented-not-modeled thresholds (T-27)
   └─ push just under the attention budget ...... stops at leaf: C-20 (attention budget is monitored with human review; thresholds stated as operational judgment, never claimed as a modeled curve — T-27 control)
```

## 6. Numbered claims

- **AT-1.** The four trees cover the highest-risk threats named in
  the opening brief (fake approval, mutated intent, prompt-injection
  egress, approval fatigue).
- **AT-2.** Every leaf in every tree names the control that stops it;
  no leaf is left unstopped and no leaf is stopped by prose alone.
- **AT-3.** The fake-approval tree rests on the session lifecycle
  (`session-lifecycle.md`): unknown, revoked, and expired sessions
  are distinct leaves because they are distinct kill points (SL-3,
  SL-14, SL-15).
- **AT-4.** The approval-fatigue tree treats the T-27 limitation
  honestly: the budget is monitored with human review, not modeled
  — the leaf control (C-20) is the compensating control, not a
  claim of modeling.
- **AT-5.** Cross-boundary attacks (e.g. injection at TB-6 aimed at a
  custody boundary at TB-11) inherit both boundaries' controls; the
  trees compose by boundary composition — no custody boundary is
  weaker than the estate's baseline.

## 7. Open points

- **P5-OP-5 — Card-rendering depth.** AT-1's "misleading card" leaf
  assumes cards render exact target+effect+scope+expiry from the
  digest-bound intent; the exact card schema and its digest-binding
  mechanics are estate implementation, out of spec scope here.
  **Needs HgX's word** only if he wants the card contract specified
  in this phase. **RESOLVED 2026-10-22 ~13:30 ET: specify the card contract in this phase — card schema and digest-binding mechanics become spec.**

## 8. Cross-references

- `threat-catalogue.md` — T-1, T-4, T-13/T-22, T-24, T-27 and the rest
  of the threat rows.
- `control-matrix.md` — control IDs C-1…C-20 with testability marks.
- `session-lifecycle.md` — the session kill points (SL-3, SL-14,
  SL-15).
- `capability-matrix.md` — CM-3 (scope change voids approval),
  `notify.hint` as the only attention action.

## 9. Version history

- **v0.1-draft — 2026-10-22.** First draft: AT-1…AT-4 trees worked to
  leaf controls C-1…C-20; claims AT-1…AT-5; P5-OP-5 recorded. Not
  ratified.
