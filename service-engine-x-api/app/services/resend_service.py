"""Resend email service."""

import os
from typing import Any

import resend


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

    resend.api_key = api_key

    client_display = company_name or signer_name

    # Build email HTML
    html_content = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 40px 20px;">
      <h1 style="font-size: 24px; font-weight: 600; color: #111; margin-bottom: 24px;">
        Proposal Signed
      </h1>

      <p style="font-size: 16px; color: #333; line-height: 1.6; margin-bottom: 16px;">
        <strong>{signer_name}</strong>{f' ({company_name})' if company_name else ''} has signed the proposal.
      </p>

      <div style="background: #f9f9f9; border-radius: 8px; padding: 20px; margin: 24px 0;">
        <p style="margin: 0 0 8px 0; font-size: 14px; color: #666;">Amount</p>
        <p style="margin: 0; font-size: 28px; font-weight: 600; color: #111;">{total}</p>
      </div>

      {f'<p style="margin: 24px 0;"><a href="{signed_pdf_url}" style="display: inline-block; background: #111; color: #fff; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 500;">Download Signed PDF</a></p>' if signed_pdf_url else ''}

      <p style="font-size: 13px; color: #888; margin-top: 32px;">
        Proposal ID: {proposal_id[:8]}
      </p>
    </div>
    """

    try:
        response = resend.Emails.send({
            "from": from_email,
            "to": to_emails,
            "subject": f"Proposal signed by {client_display}",
            "html": html_content,
        })
        return response
    except Exception:
        return None
