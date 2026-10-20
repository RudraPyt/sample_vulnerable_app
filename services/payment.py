"""Payment processing service for Sample Vulnerable App.

Demonstrates production order checkout and payment charge pipeline.
Contains a planted nested KeyError vulnerability on line 32.
"""

from typing import Any, Optional


def calculate_processing_fee(amount: float, fee_rate: float = 0.029) -> float:
    """Calculate payment gateway processing fee."""
    if amount <= 0:
        return 0.0
    return round(amount * fee_rate + 0.30, 2)


def validate_currency(currency: str) -> bool:
    """Ensure currency is supported."""
    supported = {"USD", "EUR", "GBP", "CAD", "AUD"}
    return currency.upper() in supported


def process_payment(order: dict[str, Any]) -> dict[str, Any]:
    """Process customer order payment and charge token.

    Planted bug: Line 32 accesses order["payment"]["card"]["token"] without checking
    if the payment dictionary contains the "card" key, raising KeyError on alternative
    or missing payment method payloads.
    """
    order_id = order.get("order_id", "unknown")
    amount = order.get("amount", 0.0)
    currency = order.get("currency", "USD")

    if not validate_currency(currency):
        raise ValueError(f"Unsupported currency: {currency}")

    # PLANTED BUG: Direct dictionary key navigation raises KeyError: 'card'
    # when an order has a payment block without 'card' (e.g. apple_pay, paypal, or unformatted payment).
    token = order["payment"]["card"]["token"]

    fee = calculate_processing_fee(amount)
    total_charged = round(amount + fee, 2)

    return {
        "status": "success",
        "order_id": order_id,
        "amount": amount,
        "fee": fee,
        "total_charged": total_charged,
        "transaction_id": f"tx_{order_id}_{token[:6]}",
    }
