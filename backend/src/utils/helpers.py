from datetime import datetime, timezone


def utcnow() -> datetime:
    """Naive UTC datetime (keeps comparisons consistent across DB engines)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
