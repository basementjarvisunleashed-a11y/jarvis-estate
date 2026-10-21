"""Phase 2 — attention budget tracker (control plane).

Attention is a MONITORED quantity; unspent budget is a success metric.

Budgets bound system-initiated interruptions per surface per day:
    watch   <= 5/day  (approvals and critical alerts only — contract-gated)
    phone   <= 3/day  system-initiated pulls
    tablet  unbounded but principal-initiated only (system-initiated refused)
    tv      0 — any system-initiated pull is refused
    headset 0 — any system-initiated pull is refused

Exceeding budget is refused or queued, never silently spent.
Principal-initiated pulls are never counted against any budget.
Spend is bucketed per day off the injected clock, so day rollover resets it.
"""

from common import planes
from common.planes import Plane


SURFACES = ("phone", "watch", "tablet", "tv", "headset")

# None = unbounded (tablet: principal-initiated only, so the system budget
# never applies; the pull server refuses system-initiated tablet pulls).
BUDGETS = {
    "watch": 5,
    "phone": 3,
    "tablet": None,
    "tv": 0,
    "headset": 0,
}


class BudgetTracker(planes.Component):
    """Control-plane component: tracks attention spend per surface per day."""

    plane = Plane.CONTROL

    def __init__(self, name: str, clock):
        super().__init__(name)
        self.clock = clock
        self.ledger = {}  # (surface, day) -> system-initiated pulls spent

    def _day(self) -> int:
        return self.clock.now() // 86400

    def spent(self, surface: str) -> int:
        """System-initiated pulls spent by this surface today."""
        return self.ledger.get((surface, self._day()), 0)

    def remaining(self, surface: str):
        """Budget left today. 'unbounded' for tablet."""
        budget = BUDGETS[surface]
        if budget is None:
            return "unbounded"
        return budget - self.spent(surface)

    def request(self, surface: str, initiated: str = "system",
                deferrable: bool = True) -> dict:
        """Ask to spend one unit of attention.

        Returns a verdict dict. 'allowed' spends exactly one unit;
        'queued'/'refused' spend nothing — never silently spent.
        """
        day = self._day()
        base = {"surface": surface, "initiated": initiated,
                "spent": self.spent(surface)}
        if surface not in BUDGETS:
            base.update(verdict="refused", counted=False,
                        reason="unknown surface %r" % (surface,))
            return base
        if initiated != "system":
            base.update(verdict="allowed", counted=False,
                        remaining=self.remaining(surface),
                        reason="principal-initiated pulls are never counted")
            return base
        budget = BUDGETS[surface]
        if surface == "tablet":
            base.update(verdict="refused", counted=False, remaining="unbounded",
                        reason="tablet is principal-initiated only; "
                               "system-initiated pulls are refused")
            return base
        spent = self.ledger.get((surface, day), 0)
        if spent < budget:
            self.ledger[(surface, day)] = spent + 1
            base.update(verdict="allowed", counted=True, spent=spent + 1,
                        remaining=budget - spent - 1, budget=budget,
                        reason="within budget")
            return base
        # A zero budget means never: there is nothing to queue against.
        # An exhausted positive budget is queued when deferrable.
        verdict = "queued" if (deferrable and budget > 0) else "refused"
        base.update(verdict=verdict, counted=False, remaining=0, budget=budget,
                    reason="attention budget exhausted for %s "
                           "(budget %d/day, spent %d); %s, never silently spent"
                           % (surface, budget, spent, verdict))
        return base

    def report(self) -> dict:
        """Per-surface spend plus the unspent-budget success metric.

        attention_success.unspent counts unspent units across the bounded
        surfaces (watch/phone/tv/headset); tablet is unbounded and excluded.
        """
        rows = {}
        unspent = 0
        total = 0
        for s in SURFACES:
            b = BUDGETS[s]
            sp = self.spent(s)
            if b is None:
                rows[s] = {"budget": "unbounded", "spent": sp,
                           "remaining": "unbounded", "unspent": "n/a"}
            else:
                rem = b - sp
                rows[s] = {"budget": b, "spent": sp,
                           "remaining": rem, "unspent": rem}
                unspent += rem
                total += b
        return {
            "day": self._day(),
            "surfaces": rows,
            "attention_success": {
                "unspent": unspent,
                "of_budget": total,
                "unspent_ratio": (unspent / total) if total else 1.0,
            },
        }
