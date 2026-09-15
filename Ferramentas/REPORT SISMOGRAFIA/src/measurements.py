from __future__ import annotations

import re
from typing import Any, Dict, Optional


QUALIFIER_PATTERN = re.compile(r"^\s*([<>])\s*[-+]?\d+(?:[\.,]\d+)?")


def extract_qualifier(value: Any) -> Optional[str]:
    """Return the instrument qualifier when a source value starts with < or >."""
    if value is None:
        return None
    match = QUALIFIER_PATTERN.match(str(value).replace("\u00a0", " "))
    return match.group(1) if match else None


def format_number(value: Any, digits: int = 3, comma: bool = True, qualifier: str | None = None) -> str:
    """Format a numeric value while retaining the source's measurement qualifier."""
    if value is None:
        return "N/D"
    text = f"{float(value):.{digits}f}"
    if comma:
        text = text.replace(".", ",")
    if qualifier in ("<", ">"):
        return f"{qualifier}{text}"
    return text


def format_record_value(record: Dict, field: str, digits: int = 3, comma: bool = True) -> str:
    qualifiers = record.get("numeric_qualifiers", {}) or {}
    return format_number(record.get(field), digits=digits, comma=comma, qualifier=qualifiers.get(field))
