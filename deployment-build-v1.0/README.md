# J.A.R.V.I.S. — Deployment Build v1.0 (working room, private)

Implementation of the Deployment White Paper v1.0 (2026-10-21) — the pull
architecture, the orchestral layers, the three standardized proofs, and the
complete handshake — built in the paper's phase order (§6.1).

## What it is

A faithful, stdlib-only Python implementation of the paper's normative
sections (§§2–5, Appendix A): three planes with pull-only cross-plane
rules enforced in code, the five-rule pull discipline under chaos, five
per-surface contracts with sealed refusals, the six-step handshake with
its worked trace reproduced exactly, and the S1/S2/S3 proof protocol
shape with a versioned statement registry.

## What it is not

- NOT production cryptography. Phase 4's prover/verifier is a REFERENCE
  implementation — the zero-knowledge property is NOT established.
  Production requires audited STARK/SNARK circuits (§4.3). Every
  reference file says so.
- NOT the sealed 2.0 lab volumes. This build implements only the
  deployment cut.
- NOT published anywhere. No git, no GitHub, no Dropbox, no website —
  ever. Private working-room build.
- TEST keys only. `common/keys.py` generates random keys marked
  CEREMONY-TEST; `load_keys()` refuses to load without the marker.

## Layout

    common/      seals, envelopes, intent digests (seal.py); three planes
                 + pull-only gateway enforcement (planes.py); TEST key
                 ceremony (keys.py); append-only hash-chained intent log
                 with checkpoint/rollback (log.py); injectable clock
    phase0/      Ground: ceremony, log, seal verification — 18 tests
    phase1/      Pull: protocol, long-poll, sealed denials, orchestrator
                 loop, chaos (partition/replay/clock-skew) — 27 tests
    phase2/      Orchestra: enrollment ceremony, five surface contracts,
                 attention budget — 33 tests
    phase3/      Handshake: six steps, state machine, §5.5 trace, §5.4
                 refusals — 19 tests
    phase4/      Proofs: S1/S2/S3 registry + REFERENCE prover/verifier,
                 measured budgets — 35 tests
    tests/evidence/  per-phase logs with exact counts

## How to run

    sh run-all.sh            # all 132 tests
    sh phaseN/run.sh         # one phase

Python 3 stdlib only. No network. No installation.

## Honest limits

1. Phase 4 proves the protocol shape, not zero-knowledge. Budgets are
   measured honestly (see phase4/measurements.json); the ZK property
   awaits audited circuits.
2. "Deployed" per §6.2 requires the §5.5 handshake to reproduce on the
   live system witnessed by HgX, plus a quiet week for the attention
   criterion — neither is satisfiable by this test build.
3. The execution edge is placed in the data plane (documented rationale
   in phase3/handshake.py): the paper's three NEVER columns leave it
   homeless; it verifies sealed proofs, decides nothing, pushes nothing.
4. Ambiguities found during the build are decided and documented in the
   phase evidence logs — never silently invented.
5. No doctoral phase is closed by this build. See PHASE-EXIT-MAPPING.md;
   HgX closes phases on evidence.
