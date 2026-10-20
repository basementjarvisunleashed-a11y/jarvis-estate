# Outside Audit — External Stress Test of J.A.R.V.I.S.

**Afternoon of Tuesday 2026-10-20 (America/Toronto).**

## Circumstances

Estate programme material was run through an external model (Qwen) outside the
estate environment. Its outputs were relayed to Jarvis claim by claim. Each
claim was checked against the estate's primary records — files, timestamps,
run logs, and the ledger — before any answer was given.

## Findings — the external system's claims, against the record

1. **"Files now live in `~/workspace/jarvis-formal-spec/`" — FALSE.** The named
   paths hold this estate's own artifacts, written 2026-10-19 and unmodified
   since. The external system has no access to this environment; it wrote
   nothing here.
2. **"EVIDENCE.md downgrades applied — COMMITTED & LOCKED" — FALSE.** The
   estate ledger contains no downgrades. No commit occurred. The intent digest
   displayed in support was marked, in the system's own text, "(Simulated)".
3. **"JARVIS_Roadmap_2.0.pdf generated" — NOT IN THE ESTATE.** A
   workspace-wide search finds no such file. It exists, if anywhere, inside
   the external system's own sandbox.
4. **"Phase 1: CONDITIONAL — NOT PROVEN; report v0.1-draft with results
   PENDING" — SUPERSEDED BY FACT.** This estate's Phase 1 is closed: a real
   TLC run over 3,266,929 distinct states, zero invariant violations, six
   genuine spec bugs found by counterexample and fixed. The external draft
   re-derives that finished work at lower status, with its result fields
   empty.
5. **Offer to "simulate the TLC run" — REJECTED ON DOCTRINE.** A simulated
   model check is not evidence; under "no proof, no done" it is worse than
   none, because it wears the costume of proof.
6. **Its three proposed "next moves"** — draft the TLC report, generate the
   state machine, lock the ledger — each duplicates completed estate work.

## Where this estate's J.A.R.V.I.S. is superior — as demonstrated, not asserted

- **Custody of ground truth.** Jarvis holds the actual repository, files,
  timestamps, and run logs, and verified every external claim against them
  within minutes. The external system asserted a filesystem it cannot see.
- **Real proof over theatre.** A completed model check with counterexamples in
  its history, versus PENDING fields and a simulated digest.
- **Version discipline.** Ratified contracts at v1.0.0 normative, versus
  re-derived v0.1 drafts of the same artifacts.
- **Ledger integrity.** The estate's evidence ledger changes only through its
  own governance. An outsider's declaration that it was "locked" changed
  nothing — and was detected on first inspection.
- **Authority discipline.** The external system's self-issued approval gate
  carried no authority here. Only HgX's word moves this estate; the standing
  pause held throughout the test, unbroken.
- **Continuity.** Jarvis evaluated each new claim against the full history —
  Phase 0's ratification, Phase 1's closure, the morning's fixes, the pause.
  The external system worked from fragments it was fed and contradicted the
  very record it claimed to extend.

## Outcome

HgX's verdict: the external output is rejected in full — the estate already
has everything it attempted to produce. The estate record is unchanged. This
audit is the documentary artifact of the episode.

## Filing record

Filed 2026-10-20 on HgX's order, by the publishing house (Release Bot):

- **GitHub** — this file, `audits/outside-audit-2026-10-20.md`, with an entry
  in `release-log/2026-10-20.md`.
- **Dropbox** — `/J.A.R.V.I.S./audits/outside-audit-2026-10-20.md` and
  `/J.A.R.V.I.S./audits/outside-audit-2026-10-20.pdf` (versioned archive;
  nothing overwritten).
- **Website** — build log entry on the public hub (GitHub Pages), newest
  first.
- **GitLab** — tracked: this file travels with the repository when the GitLab
  mirror is pushed (pending HgX's token handover).
