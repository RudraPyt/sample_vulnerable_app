# Sample Vulnerable Application (DevPulse Target Repo)

This repository serves as the target demonstration service for DevPulse autonomous incident triage and patch verification.

It is a lightweight Python application containing two intentional, realistic edge-case bugs and their corresponding regression tests.

---

## Repository Structure

```
sample_vulnerable_app/
├── README.md
├── requirements.txt
├── services/
│   ├── payment.py    # Order checkout & card charge service (contains planted KeyError)
│   └── auth.py       # Session token validation service (contains planted datetime TypeError)
└── tests/
    ├── test_payment.py
    └── test_auth.py
```

---

## Baseline Test Suite Status

Running `pytest` against this codebase results in **exactly 2 failures** (one per planted bug) with all other tests passing:

```bash
pytest -v
```

```text
sample_vulnerable_app/tests/test_auth.py::test_generate_session_payload PASSED
sample_vulnerable_app/tests/test_auth.py::test_has_permission PASSED
sample_vulnerable_app/tests/test_auth.py::test_verify_auth_token_missing_data PASSED
sample_vulnerable_app/tests/test_auth.py::test_verify_token_with_iso_utc_timestamp FAILED
sample_vulnerable_app/tests/test_payment.py::test_calculate_processing_fee PASSED
sample_vulnerable_app/tests/test_payment.py::test_validate_currency PASSED
sample_vulnerable_app/tests/test_payment.py::test_process_payment_valid_card PASSED
sample_vulnerable_app/tests/test_payment.py::test_process_payment_missing_card_details FAILED

========================= 2 failed, 6 passed in 0.14s =========================
```

---

## Preset Incident Traces for DevPulse Agent

### Bug 1: Payment API Crash (500 Error / KeyError: 'card')

**Trigger**: An order payment is submitted without explicit credit card details (e.g. digital wallet or alternative payment method), causing direct dictionary navigation to fail on missing key.

**Ready-Made Error Traceback**:
```text
Traceback (most recent call last):
  File "services/payment.py", line 39, in process_payment
    token = order["payment"]["card"]["token"]
KeyError: 'card'
```

---

### Bug 2: Auth Token Expiry Bug (TypeError: naive vs. aware datetime)

**Trigger**: An authentication token carries an ISO 8601 UTC timestamp with timezone offset (`+00:00`), causing Python's datetime comparison with naive `datetime.now()` to fail.

**Ready-Made Error Traceback**:
```text
Traceback (most recent call last):
  File "services/auth.py", line 51, in verify_auth_token
    if now > expires_at:
TypeError: can't compare offset-naive and offset-aware datetimes
```
