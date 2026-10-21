"""Injectable clock. Real time in production paths; FakeClock for tests
and chaos (clock-skew injection, paper §6.4)."""


class Clock:
    def now(self) -> int:
        import time
        return int(time.time())


class FakeClock(Clock):
    def __init__(self, start: int = 1_700_000_000):
        self.t = start

    def now(self) -> int:
        return self.t

    def advance(self, seconds: int):
        self.t += seconds

    def skew(self, seconds: int):
        """Inject clock skew (chaos testing)."""
        self.t += seconds
