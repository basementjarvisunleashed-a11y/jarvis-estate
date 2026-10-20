---
name: "usage-router"
description: "A cheap decision gate before expensive work: consult before the live browser, multi-source research, retrying a failed approach, or spawning a subagent. Local policy by default (shadow mode, kill switch); an optional TypeSafe Jev backend can be enabled later via the Secure Vault. Adapted 2026-10-07 from the Jev usage-router pattern into the J.A.R.V.I.S. operating system."
---

# Usage Router

## Purpose
Stop expensive work before it starts. Before the live browser, deep research, a retry, or a new subagent, the router answers one question: *is this the cheapest reliable path to the result?* It is a gate, not a brain — the operator's approvals and the estate's existing rules still govern everything consequential.

Design note: unlike the Grok Bot original, this skill does **not** require the TypeSafe Jev API. The decision policy below runs locally at zero cost and zero data egress. A Jev backend is optional (see below) and never the default.

## When to Consult
Consult the router **before**:
- `browser.spawn_task` or `browser.deep_research` (expensive, slow, visible)
- Retrying an approach that just failed
- Spawning a subagent (`subagent.spawn`)
- Loading several specialized skills for a single task

Do **not** consult for: answering from memory or context, a single `browser.search`, reading files, or anything the operator asked to do directly and simply.

## Kill Switch
Check first, every time. Skip the router entirely and proceed normally when:
- `~/workspace/usage-router/config.json` has `"enabled": false`, or
- the operator says `bypass router`, `no router`, or `skip the gate`.

## Modes
- **shadow** (default): evaluate, log the recommendation, then continue on normal judgment. The log is the product — it builds trust in the gate.
- **active**: honor the router's action below.

the operator flips modes by saying so ("router active", "router shadow"). Current mode lives in `config.json`.

## The Decision State
Build this compact state before deciding:
```json
{
  "goal": "what the operator wants",
  "kind": "chat|lookup|research|browser|coding|write|account",
  "cached_artifact": false,
  "cached_note": "freshness and scope, if any",
  "prior_error": "last error, if retrying",
  "same_error_count": 0,
  "sources_found": 0,
  "constraints": "limits that apply"
}
```

## Local Decision Policy
Apply in order; first match wins:

1. **Irreversible actions escalate, always.** Anything that sends, spends, publishes, or deletes goes to the operator regardless of mode. The router never approves consequences.
2. **Retry budget.** Same operation, same error: at most **2 retries**, then `escalate` (try a fundamentally different approach, or ask the operator). Increment `same_error_count` per identical failure.
3. **Loop detection.** The same action proposed 3 times without measurable progress → `deny`, escalate to the operator with what was tried.
4. **Cache preference.** If a cached artifact or note answers the goal and is fresh → `use-cache`. Never re-fetch what is already known.
5. **Subagent gating.** Spawn only when the work is multi-step, independent of the chat reply, and long-running. Quick or single-step work → `deny`, do it directly.
6. **Browser gating.** `browser.search` for discovery is cheap — proceed. The live browser / deep research only when the answer needs current state (prices, availability, account data, live pages). Curiosity browsing → `deny`.
7. **Deferral.** If the goal is vague and the cost is high → `defer`: ask the operator one focused question first.

Actions: `proceed` | `use-cache` | `defer` | `escalate` | `deny`.

## Logging
Every consultation appends one JSON line to `~/workspace/usage-router/logs/router-YYYY-MM-DD.jsonl`:
`{ts, mode, state, recommendation, action_taken, note}`. In shadow mode, `action_taken` records what normal judgment did instead. the operator may ask "show me the router log" any time.

## Optional Jev Backend
Only if the operator explicitly asks for it:
1. He creates a TypeSafe AI API key himself at the provider's official site.
2. The key is stored via the **Secure Vault** flow — never in chat, never in a file, never in `config.json`.
3. The router sends **only** the compact decision state above — no names, no message contents, no PII.
4. Any backend failure → fall back to the local policy immediately and log the fallback.

Until then, `"backend": "local"` stays as it is, and the skill is fully functional without it.

## Operating Rules
- Jarvis manner: formal, precise, dry British wit. Address the principal ONLY as the operator.
- The router advises; it never overrides the operator, and never touches approvals.
- Prefer the cheapest reliable path, but never a cheap wrong one — a wrong fast answer is the most expensive kind.
- Keep the policy small. If a rule never fires, propose removing it.
