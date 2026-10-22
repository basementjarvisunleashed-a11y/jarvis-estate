# Phase 6 — Jev Evaluation Payment Gate

**Written:** 2026-10-22 ~13:47 ET, on HgX's direct word ("documented that we have to pay now to move ahead in the next phase").
**Status:** payment required; trial approved and parked.

## What the money is for

Phase 6 (Router Optimality) exit criterion, ROADMAP.md §9 verbatim: "Jev evaluated
if approved." HgX approved the Jev trial 2026-10-22 ~13:36 ET (P6-OP-7). The trial
evaluates the TypeSafe Jev backend against the local seven-rule policy on the
router decision corpus — the one comparison money can buy: whether the paid
backend beats the free local policy.

## What is required

1. A TypeSafe AI API key (HgX creates it himself at console.typesafe.ai).
2. A funded TypeSafe account — API calls are billed per input token
   ($0.042 per million input tokens at list price; output free).

## Current status (verified against HgX's console, 2026-10-22 ~13:41 ET)

- Signed in at console.typesafe.ai with Google — done.
- API key minted — done.
- **Available credits: $0.00.** The third-party claim of an automatic $5 new-user
  credit did not hold for this account.
- Key **not yet** placed in the Secure Vault.
- **Funding deferred to 2026-10-23** on HgX's word ("we'll do it tomorrow").

## Standing position until funded

- The trial is approved and parked. The L2 harness is Jev-ready (pluggable
  backend interface, refusal verified: no approval/key → `JevNotApproved`,
  nothing sent, no spend).
- No API spend, no data egress, no endpoint called until the key is in the
  vault and the account is funded.
- Nothing breaks. Phase 6's other work (stages 1–2, weighted comparison on the
  real corpus, live labeled-volume accumulation) proceeds regardless.

## To move ahead

1. Fund the account at console.typesafe.ai → Billing → Add funds.
2. Place the API key via the Secure Vault flow (never in chat).
3. The trial runs on HgX's word once both are in place.
