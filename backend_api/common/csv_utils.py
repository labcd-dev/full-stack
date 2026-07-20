"""Shared helpers for CSV export."""

from __future__ import annotations

import csv
import io
from typing import Any, Iterable, Sequence


def rows_to_csv(rows: Iterable[dict[str, Any]], fieldnames: Sequence[str]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()
