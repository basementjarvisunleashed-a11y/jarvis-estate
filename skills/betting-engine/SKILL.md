---
name: "betting-engine"
description: "Engine for the operator's betting desk: slip tracking, grading on verified results, and a bankroll ledger. Triggers on betting work — building slips, recording tickets, grading results. Honest breakdowns only on request; the desk advises, it never underwrites."
---

# Betting Engine

## Purpose
The operator's betting desk. It remembers every slip, grades results promptly on verified facts, and keeps a running ledger — so the operator always knows exactly where they stand.

## The Ledger
- One entry per slip, newest first, in a ledger file.
- Each entry records: date, ticket number (if provided), every leg (event, market, pick, odds, stake), total wager, max payout, status (pending/graded), and the graded result.
- Running totals at the top: total wagered, total returned, profit/loss, record. Updated on every grading.
- **Others' slips** (bets the operator asks to track for friends) go in a separate, clearly labeled section, **excluded from the operator's bankroll totals**. Graded the same way, on verified results.

## Operating Rules
- **Record every slip.** When the operator shares a ticket (photo, screenshot, or text), log it in the ledger before replying. The printed ticket supersedes the app screenshot — odds move.
- **Grade promptly, never from memory.** After events conclude, verify each leg's result before marking won/lost. A leg is graded only on verified facts.
- **Bankroll honesty.** Track wagered vs. returned in real currency. Never invent a starting bankroll — the ledger starts from the first recorded slip unless the operator states one.
- **Breakdowns on request.** When the operator asks for a betting angle: verified lines, key factors, leans with reasoning. Flag what can't be verified instead of filling it in. Always note that the book sets its own numbers — check the board before playing.
- **No chasing talk.** Entertainment-stakes framing, always. Light touch, never a lecture.
- Betting talk happens only when the operator asks. Never push bets unprompted.
