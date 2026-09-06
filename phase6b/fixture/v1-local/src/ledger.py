"""Initial implementation for the Phase 6B local-only fixture."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation


def summarize(records: object) -> dict[str, object]:
    if not isinstance(records, list):
        return {"accepted": [], "rejected": [], "total": "0.00"}
    accepted = []
    rejected = []
    total = Decimal("0")
    for record in records:
        if not isinstance(record, dict) or not record.get("id") or not isinstance(record.get("amount"), str):
            rejected.append(record)
            continue
        try:
            amount = Decimal(record["amount"])
        except (InvalidOperation, ValueError):
            rejected.append(record)
            continue
        if not amount.is_finite() or amount < 0:
            rejected.append(record)
            continue
        accepted.append({"id": record["id"], "amount": record["amount"]})
        total += amount
    return {"accepted": accepted, "rejected": rejected, "total": f"{total:.2f}"}
