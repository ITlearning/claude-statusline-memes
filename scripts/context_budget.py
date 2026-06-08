"""Pure helpers for the context-budget statusline additions. Stdlib only, no I/O on import."""


def should_warn(used_percentage, threshold=80.0):
    """True when context usage % is at/above threshold."""
    if used_percentage is None:
        return False
    try:
        return float(used_percentage) >= float(threshold)
    except (TypeError, ValueError):
        return False
