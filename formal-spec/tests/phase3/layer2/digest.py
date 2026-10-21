"""Eight-field approval digest — ratified spec/approval-digest.md.

Phase 2 Q3 ruling (HgX): eight fields — the paper text — intent_id and
work_id included. Phase 2 Q4 ruling (HgX): the draft's concrete canonical
procedure — Unicode code-point key order, exact (',', ':') separators,
UTF-8, ensure_ascii=False. SHA-256.

This module is a test-side reimplementation of the ratified procedure so
the Layer 2 tests can compute digests independently of the orchestrator
model (both must agree; the tests assert the agreement).
"""

import hashlib
import json

# The eight bound fields, per spec/approval-digest.md line 10.
INTENT_FIELDS = ("intent_id", "work_id", "action", "target", "effect",
                 "scope", "revision", "expiry")


def canonical_payload(record):
    """The exact 249-byte-style canonical form (ratified procedure)."""
    bound = {k: record[k] for k in INTENT_FIELDS}
    return json.dumps(bound, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def approval_digest(record):
    """sha256 hex of the canonical payload."""
    return hashlib.sha256(canonical_payload(record)).hexdigest()
