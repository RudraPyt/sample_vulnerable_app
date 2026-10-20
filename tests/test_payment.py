"""Tests for payment service in Sample Vulnerable App.

Contains passing tests for normal payment flows, and exactly ONE failing test
(test_process_payment_missing_card_details) that triggers the planted KeyError: 'card'.
"""

import pytest
import sys
from pathlib import Path

# Add project root to sys.path so services can be imported cleanly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.payment import (
    process_payment,
    calculate_processing_fee,
    validate_currency,
)


def test_calculate_processing_fee():
    """Verify standard processing fee calculation."""
    assert calculate_processing_fee(100.0) == 3.20  # 100 * 0.029 + 0.30
    assert calculate_processing_fee(0.0) == 0.0


def test_validate_currency():
    """Verify supported and unsupported currency codes."""
    assert validate_currency("USD") is True
    assert validate_currency("EUR") is True
    assert validate_currency("JPY") is False


def test_process_payment_valid_card():
    """Verify successful payment processing when full card token payload is provided."""
    order = {
        "order_id": "ord_1001",
        "amount": 50.0,
        "currency": "USD",
        "payment": {
            "method": "credit_card",
            "card": {
                "token": "tok_visa_4242",
                "last4": "4242",
            },
        },
    }
    result = process_payment(order)
    assert result["status"] == "success"
    assert result["order_id"] == "ord_1001"
    assert result["amount"] == 50.0
    assert result["transaction_id"].startswith("tx_ord_1001_tok_vi")


def test_process_payment_missing_card_details():
    """PLANTED FAILING TEST: Triggers KeyError: 'card' when payment dictionary has no card key."""
    order = {
        "order_id": "ord_1002",
        "amount": 75.0,
        "currency": "USD",
        "payment": {
            "method": "wallet",
            # 'card' key is omitted, causing order['payment']['card'] to raise KeyError
        },
    }
    # This call raises KeyError: 'card' on line 32 of services/payment.py
    result = process_payment(order)
    assert result["status"] == "success"
