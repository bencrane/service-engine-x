"""Resend email service."""

import os
from typing import Any


def send_proposal_signed_email(
    to_emails: list[str],
    from_email: str,
    signer_name: str,
    company_name: str | None,
    total: str,
    signed_pdf_url: str | None,
    proposal_id: str,
) -> dict[str, Any] | None:
    """
    Send email notification when a proposal is signed.

    Returns the Resend response or None if sending fails.
    """
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        return None

    try:
        import resend
    except ImportError:
        return None

    resend.api_key = api_key

    client_display = company_name or signer_name

    # Build email HTML
    html_content = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 40px 20px;">
      <h1 style="font-size: 24px; font-weight: 600; color: #111; margin-bottom: 24px;">
        Agreement Signed - ACH Payment Details
      </h1>

      <p style="font-size: 16px; color: #333; line-height: 1.6; margin-bottom: 16px;">
        <strong>{signer_name}</strong>{f' ({company_name})' if company_name else ''} has signed the agreement.
      </p>

      <div style="background: #f9f9f9; border-radius: 8px; padding: 20px; margin: 24px 0;">
        <p style="margin: 0 0 8px 0; font-size: 14px; color: #666;">Amount Due</p>
        <p style="margin: 0; font-size: 28px; font-weight: 600; color: #111;">{total}</p>
      </div>

      <div style="background: #f0f9f0; border: 1px solid #22c55e; border-radius: 8px; padding: 24px; margin: 24px 0;">
        <p style="margin: 0 0 16px 0; font-size: 16px; font-weight: 600; color: #111;">ACH Payment Details</p>

        <p style="margin: 0 0 4px 0; font-size: 12px; color: #666; text-transform: uppercase;">Account Name</p>
        <p style="margin: 0 0 16px 0; font-size: 15px; color: #111; font-weight: 500;">Modern Full, LLC</p>

        <p style="margin: 0 0 4px 0; font-size: 12px; color: #666; text-transform: uppercase;">Routing Number</p>
        <p style="margin: 0 0 16px 0; font-size: 15px; color: #111; font-weight: 500;">091311229</p>

        <p style="margin: 0 0 4px 0; font-size: 12px; color: #666; text-transform: uppercase;">Account Number</p>
        <p style="margin: 0 0 16px 0; font-size: 15px; color: #111; font-weight: 500;">202314840766</p>

        <p style="margin: 0 0 4px 0; font-size: 12px; color: #666; text-transform: uppercase;">Bank</p>
        <p style="margin: 0; font-size: 15px; color: #111; font-weight: 500;">Choice Financial Group<br><span style="font-weight: 400; color: #666;">4501 23rd Avenue S, Fargo, ND 58104</span></p>
      </div>

      {f'<p style="margin: 24px 0;"><a href="{signed_pdf_url}" style="display: inline-block; background: #111; color: #fff; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 500;">Download Agreement</a></p>' if signed_pdf_url else ''}

      <p style="font-size: 13px; color: #888; margin-top: 32px;">
        Agreement ID: {proposal_id[:8]}
      </p>
    </div>
    """

    try:
        response = resend.Emails.send({
            "from": from_email,
            "to": to_emails,
            "subject": f"ACH Payment Details - Agreement signed by {client_display}",
            "html": html_content,
        })
        return response
    except Exception:
        return None
