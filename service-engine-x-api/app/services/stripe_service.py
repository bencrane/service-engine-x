"""Stripe payment integration service."""

from typing import Any

import stripe


def create_checkout_session(
    api_key: str,
    line_items: list[dict[str, Any]],
    success_url: str,
    cancel_url: str,
    metadata: dict[str, str],
    customer_email: str | None = None,
) -> dict[str, Any]:
    """
    Create a Stripe Checkout session.

    Args:
        api_key: Stripe secret API key for the organization
        line_items: List of line items in Stripe format
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect if payment is cancelled
        metadata: Key-value pairs to attach to the session
        customer_email: Optional email to prefill in checkout

    Returns:
        Dict with checkout_url and session_id
    """
    stripe.api_key = api_key

    session_params: dict[str, Any] = {
        "payment_method_types": ["card"],
        "line_items": line_items,
        "mode": "payment",
        "success_url": success_url,
        "cancel_url": cancel_url,
        "metadata": metadata,
    }

    if customer_email:
        session_params["customer_email"] = customer_email

    session = stripe.checkout.Session.create(**session_params)

    return {
        "checkout_url": session.url,
        "session_id": session.id,
    }


def build_line_items_from_proposal(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Convert proposal items to Stripe line_items format.

    Args:
        items: List of proposal items with name, description, price

    Returns:
        List of Stripe-formatted line items
    """
    line_items = []

    for item in items:
        price_cents = int(float(item.get("price", 0)) * 100)

        line_item = {
            "price_data": {
                "currency": "usd",
                "unit_amount": price_cents,
                "product_data": {
                    "name": item.get("name", "Service"),
                },
            },
            "quantity": 1,
        }

        # Add description if available
        description = item.get("description")
        if description:
            line_item["price_data"]["product_data"]["description"] = description[:500]

        line_items.append(line_item)

    return line_items


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str,
) -> dict[str, Any] | None:
    """
    Verify Stripe webhook signature and return the event.

    Args:
        payload: Raw request body bytes
        signature: Stripe-Signature header value
        secret: Webhook signing secret

    Returns:
        Parsed event dict if signature is valid, None otherwise
    """
    try:
        event = stripe.Webhook.construct_event(payload, signature, secret)
        return event
    except stripe.SignatureVerificationError:
        return None
    except ValueError:
        return None
