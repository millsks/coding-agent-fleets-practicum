"""Rough context-window arithmetic."""

CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    """Estimate tokens with the common rule of thumb of about four characters per token for English and code.

    Real tokenizers differ; use this for budgeting, never for billing.

    Args:
        text: Any text.

    Returns:
        Approximate token count, at least 1 for non-empty text.
    """
    return 0 if not text else max(1, round(len(text) / CHARS_PER_TOKEN))
