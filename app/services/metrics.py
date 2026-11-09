# app/services/metrics.py — Word counting, compression ratio, cap compliance

import re
from typing import Literal


class MetricsService:
    """
    Word count and compression metrics.

    Word count convention: split on whitespace, filter empty strings.
    This matches typical notebook conventions. If the notebook uses a specific
    tokenizer-based count, this should be updated to match exactly.
    """

    WORD_SPLIT_PATTERN = re.compile(r"\s+")

    def count_words(self, text: str) -> int:
        """Count words by splitting on whitespace."""
        if not text or not text.strip():
            return 0
        words = self.WORD_SPLIT_PATTERN.split(text.strip())
        return len([w for w in words if w])

    def compression_ratio(self, source_words: int, summary_words: int) -> float:
        """Calculate compression ratio as percentage."""
        if source_words == 0:
            return 0.0
        return round((summary_words / source_words) * 100, 2)

    def within_cap(self, actual_ratio: float, max_threshold: int) -> bool:
        """Check if actual compression ratio is within the maximum threshold."""
        return actual_ratio <= max_threshold

    def cap_status(self, actual_ratio: float, max_threshold: int) -> Literal["within", "exceeds"]:
        """Return human-readable cap status."""
        return "within" if self.within_cap(actual_ratio, max_threshold) else "exceeds"

    def format_ratio(self, actual_ratio: float) -> str:
        """Format compression ratio for display."""
        return f"{actual_ratio:.1f}%"