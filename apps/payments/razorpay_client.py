"""Razorpay client wrapper.

If razorpay SDK is not installed (or keys are not configured), the helper
falls back to a mock that creates a local order id. This lets the platform
run end-to-end in development without external keys.
"""
from django.conf import settings

try:
    import razorpay  # type: ignore
    _client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,
                                     settings.RAZORPAY_KEY_SECRET)) \
        if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET else None
except ImportError:
    razorpay = None
    _client = None


def is_configured():
    """True if a real Razorpay client is available."""
    return _client is not None


def create_order(amount_in_paise, currency='INR', receipt='', notes=None):
    """Create a Razorpay order. Returns a dict with at least 'id'.

    In mock mode (dev), returns a fake order id starting with 'mock_'.
    """
    if _client is None:
        return {
            'id': f'mock_order_{abs(hash((amount_in_paise, receipt)))}',
            'amount': amount_in_paise,
            'currency': currency,
            'status': 'created',
            'mock': True,
        }
    data = {
        'amount': amount_in_paise,
        'currency': currency,
        'receipt': receipt or None,
        'notes': notes or {},
    }
    return _client.order.create(data=data)


def verify_payment(order_id, payment_id, signature):
    """Verify the payment signature returned by Razorpay checkout."""
    if _client is None:
        # Mock: accept all 'mock_*' ids
        return order_id.startswith('mock_') and bool(payment_id)
    try:
        _client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature,
        })
        return True
    except Exception:
        return False
