"""Phase 4 — Zero-knowledge proofs (paper §4).

=====================================================================
REFERENCE IMPLEMENTATION — NOT PRODUCTION CRYPTOGRAPHY.
=====================================================================

Real STARK/SNARK circuits are sealed-lab depth and out of scope for a
stdlib build. This module implements the EXACT protocol shape, the
versioned statement registry contract, and a REFERENCE prover/verifier
so the wire shape, the audit trail, and the deployment budgets (§4.4)
can be exercised honestly. The zero-knowledge property is NOT
established for this reference: the blinded opening is reversible by
the verifier, and the statement predicate is evaluated by the (honest)
prover and attested in the sealed transcript. Production requires
audited STARK/SNARK circuits per §4.3 (STARKs preferred: no trusted
setup).

Honest boundaries (§4.5): a proof proves the statement, not the data's
truth. Proofs compose with seals (see S2: the approval envelope's seal
must verify before the prover will attest); they do not replace them.

Protocol shape (every proof): commit -> challenge -> respond -> verify.
Fiat-Shamir makes it non-interactive: challenge = SHA-256(transcript).
The verifier learns one bit — the statement is true — and nothing else
(claimed by the shape; not established for the reference — see above).

The three standardized statements — exactly these three, no more:
  S1: "This value exceeds threshold T in sealed baseline B"
      (variance-gate alerts without exposing the baseline)
  S2: "An approval exists for intent digest D"
      (actuation without re-showing the approval)
  S3: "This payload satisfies policy P"
      (execution without exposing the payload)
"""

import hashlib
import hmac
import secrets

from common import seal as _seal

# ---------------------------------------------------------------------
# REFERENCE marker — every proof object carries it on the wire.
# ---------------------------------------------------------------------
REFERENCE_TAG = "REFERENCE-NOT-PRODUCTION-CRYPTOGRAPHY"

# Deployment parameters (§4.4) — measured honestly by phase4/test_phase4.py.
FRESHNESS_WINDOW_S = 300          # proofs bind ts + nonce; stale rejected
PROOF_SIZE_BUDGET_BYTES = 200 * 1024   # STARK budget
SNARK_SIZE_BUDGET_BYTES = 2 * 1024     # SNARK budget (informational here)
PROVING_TIME_BUDGET_S = 30
VERIFY_TIME_BUDGET_MS = 100

STATEMENT_IDS = ("S1", "S2", "S3")

S1_TEXT = "This value exceeds threshold T in sealed baseline B"
S2_TEXT = "An approval exists for intent digest D"
S3_TEXT = "This payload satisfies policy P"


class ProofError(Exception):
    """Base class for Phase 4 failures. Fail closed."""


class ProveError(ProofError):
    """The honest prover refuses: false statement or stale circuit."""


class RegistryError(ProofError):
    """Statement registry misuse (unknown id, bad version, ...)."""


# ---------------------------------------------------------------------
# REFERENCE policy table for S3 (reference evaluator binding).
# Production binds the policy to the circuit; here the digest is over
# the policy id only — documented, not hidden.
# ---------------------------------------------------------------------
_POLICIES = {}


def policy_digest(policy_id: str) -> str:
    """REFERENCE policy digest: SHA-256 over the canonical policy id."""
    return _seal.sha256_hex(_seal.canonical({"policy_id": str(policy_id)}))


def register_policy(policy_id: str, evaluator) -> str:
    """Register a REFERENCE policy evaluator. Returns its digest."""
    if not callable(evaluator):
        raise ProofError("policy evaluator must be callable")
    _POLICIES[str(policy_id)] = evaluator
    return policy_digest(policy_id)


def _predicate_s1(public: dict, witness: dict, context) -> bool:
    """S1: value exceeds T and is tied to the sealed baseline B."""
    try:
        v = witness["value"]
        return (isinstance(v, (int, float)) and not isinstance(v, bool)
                and v > public["threshold"]
                and witness["baseline_digest"] == public["baseline_digest"])
    except (KeyError, TypeError):
        return False


def _predicate_s2(public: dict, witness: dict, context) -> bool:
    """S2: a sealed approval exists binding intent digest D.

    The approval envelope's seal must verify with the governance seal
    key (proofs compose with seals, §4.5) and its content must bind D.
    The approval content itself is never revealed to the verifier.
    """
    try:
        key = (context or {}).get("seal_key")
        if not isinstance(key, (bytes, bytearray)):
            return False
        env = witness["approval"]
        if not _seal.verify_envelope(bytes(key), env):
            return False
        content = env["content"]
        return (content.get("intent_digest") == public["intent_digest"]
                and witness.get("intent_digest") == public["intent_digest"])
    except (KeyError, TypeError, AttributeError):
        return False


def _predicate_s3(public: dict, witness: dict, context) -> bool:
    """S3: the payload satisfies policy P (REFERENCE evaluator)."""
    try:
        pid = public["policy_id"]
        if public.get("policy_digest") != policy_digest(pid):
            return False
        evaluator = _POLICIES.get(str(pid))
        if evaluator is None:
            return False
        return (witness.get("policy_id") == pid
                and bool(evaluator(witness["payload"])))
    except (KeyError, TypeError):
        return False


# Statement table: exactly the three standardized statements, no more.
STATEMENTS = {
    "S1": {"text": S1_TEXT, "predicate": _predicate_s1},
    "S2": {"text": S2_TEXT, "predicate": _predicate_s2},
    "S3": {"text": S3_TEXT, "predicate": _predicate_s3},
}


# ---------------------------------------------------------------------
# REFERENCE Fiat-Shamir proof-of-knowledge of the witness preimage.
# ---------------------------------------------------------------------
def _mask(challenge_hex: str) -> bytes:
    return hashlib.sha256(
        ("ZK4-MASK-v1:" + challenge_hex).encode("utf-8")).digest()


def _xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def _commitment(statement_id: str, version: int, witness_digest: str,
                nonce_hex: str) -> str:
    return _seal.sha256_hex(_seal.canonical(
        ["ZK4-COMMIT-v1", statement_id, int(version),
         witness_digest, nonce_hex]))


def _fiat_shamir_challenge(statement_id: str, version: int, commitment: str,
                           public: dict, ts: int, proof_nonce: str) -> str:
    """challenge = SHA-256(transcript): commit -> challenge, non-interactive."""
    return _seal.sha256_hex(_seal.canonical(
        ["ZK4-FIAT-SHAMIR-v1", statement_id, int(version),
         commitment, public, int(ts), proof_nonce]))


def prove(statement_id: str, version: int, public: dict, witness: dict,
          registry, clock, context: dict = None) -> dict:
    """REFERENCE prover. commit -> challenge -> respond.

    The honest prover evaluates the statement predicate itself and
    REFUSES (raises ProveError) for a false statement or a superseded
    circuit version — fail closed on both sides of the wire.
    """
    if statement_id not in STATEMENTS:
        raise ProveError("unknown statement %r" % (statement_id,))
    if registry.current_version(statement_id) != int(version):
        raise ProveError(
            "circuit v%s is not current for %s (current v%s)"
            % (version, statement_id,
               registry.current_version(statement_id)))
    predicate = STATEMENTS[statement_id]["predicate"]
    if not predicate(public, witness, context):
        raise ProveError(
            "statement %s is FALSE for this witness — prover refuses"
            % statement_id)

    witness_digest = _seal.sha256_hex(_seal.canonical(witness))
    nonce_hex = secrets.token_bytes(32).hex()
    commitment = _commitment(statement_id, version, witness_digest, nonce_hex)

    ts = int(clock.now())
    proof_nonce = secrets.token_hex(16)
    challenge = _fiat_shamir_challenge(statement_id, version, commitment,
                                       public, ts, proof_nonce)

    # respond: blinded opening of the commitment (REFERENCE: reversible).
    masked_opening = _xor(bytes.fromhex(nonce_hex),
                          _mask(challenge)).hex()

    return {
        "reference": REFERENCE_TAG,
        "statement_id": statement_id,
        "statement_text": STATEMENTS[statement_id]["text"],
        "circuit_version": int(version),
        "public": public,
        "commitment": commitment,
        "challenge": challenge,
        "witness_digest": witness_digest,
        "masked_opening": masked_opening,
        "ts": ts,
        "proof_nonce": proof_nonce,
        "attestation": True,  # prover asserts the predicate evaluated true
    }


def proof_size_bytes(proof: dict) -> int:
    """Wire size of the canonical proof (§4.4 proof-size budget)."""
    return len(_seal.canonical(proof))


class Verifier:
    """REFERENCE verifier. verify: checks the response against the
    commitment and the public statement.

    Holds the replay cache: each proof_nonce is accepted at most once.
    """

    def __init__(self, registry, clock):
        self.registry = registry
        self.clock = clock
        self.seen_proof_nonces = set()

    def reset_replay_cache(self):
        self.seen_proof_nonces = set()

    def verify(self, proof: dict) -> bool:
        """Returns True iff the proof is accepted. Never raises."""
        try:
            sid = proof["statement_id"]
            version = int(proof["circuit_version"])
            # 1. versioned registry: superseded circuits rejected.
            if not self.registry.is_current(sid, version):
                return False
            public = proof["public"]
            ts = int(proof["ts"])
            proof_nonce = str(proof["proof_nonce"])
            if proof.get("attestation") is not True:
                return False
            # 2. challenge must equal SHA-256(transcript) (Fiat-Shamir).
            expected_challenge = _fiat_shamir_challenge(
                sid, version, proof["commitment"], public, ts, proof_nonce)
            if not hmac.compare_digest(str(proof["challenge"]),
                                       expected_challenge):
                return False
            # 3. response must open the commitment.
            nonce = _xor(bytes.fromhex(str(proof["masked_opening"])),
                         _mask(expected_challenge)).hex()
            expected_commitment = _commitment(
                sid, version, str(proof["witness_digest"]), nonce)
            if not hmac.compare_digest(str(proof["commitment"]),
                                       expected_commitment):
                return False
            # 4. freshness: ts + nonce bound, 300 s window (§4.4).
            if abs(int(self.clock.now()) - ts) > FRESHNESS_WINDOW_S:
                return False
            # 5. replay: one acceptance per proof_nonce.
            if proof_nonce in self.seen_proof_nonces:
                return False
            self.seen_proof_nonces.add(proof_nonce)
            return True
        except (KeyError, TypeError, ValueError, AttributeError):
            return False
