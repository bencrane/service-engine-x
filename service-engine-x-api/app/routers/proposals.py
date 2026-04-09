"""Proposals API router."""

import hashlib
import json
import secrets
import string
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse

from app.auth.dependencies import AuthContext, get_current_org
from app.config import settings
from app.database import get_supabase
from app.utils import format_currency
from app.utils.storage import upload_proposal_pdf
from app.services.stripe_service import (
    build_line_items_from_proposal,
    create_checkout_session,
    verify_webhook_signature,
)
from app.services.resend_service import send_proposal_signed_email, send_proposal_email
from app.models.proposals import (
    PROPOSAL_STATUS_MAP,
    CreateProposalRequest,
    ProposalItemResponse,
    ProposalListItem,
    ProposalListLinks,
    ProposalListMeta,
    ProposalListMetaLink,
    ProposalListResponse,
    ProposalResponse,
)

router = APIRouter(prefix="/api/proposals", tags=["Proposals"])


# Order status map for sign endpoint
ORDER_STATUS_MAP: dict[int, str] = {
    0: "Unpaid",
    1: "In Progress",
    2: "Completed",
    3: "Cancelled",
    4: "On Hold",
}

def generate_order_number() -> str:
    """Generate an 8-character alphanumeric order number."""
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(8))


def generate_proposal_html(
    proposal: dict[str, Any],
    items: list[dict[str, Any]],
    org_name: str = "Service Engine X",
) -> str:
    """Generate HTML for the proposal PDF."""
    client_name = f"{proposal.get('client_name_f', '')} {proposal.get('client_name_l', '')}".strip()
    client_company = proposal.get("client_company") or ""
    client_email = proposal.get("client_email", "")
    proposal_date = datetime.now(timezone.utc).strftime("%B %d, %Y")
    total = float(proposal.get("total", 0))
    formatted_total = f"${total:,.2f}"
    notes = proposal.get("notes") or ""

    # Build items HTML
    items_html = ""
    for item in items:
        item_name = item.get("name", "Project")
        item_desc = item.get("description", "")
        item_price = float(item.get("price", 0))
        items_html += f"""
        <div class="item">
            <div class="item-row">
                <span class="item-name">{item_name}</span>
                <span class="item-price">${item_price:,.0f}</span>
            </div>
            <p class="item-description">{item_desc}</p>
        </div>
        """

    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Proposal for {client_company or client_name}</title>
    <style>
        @page {{
            size: letter;
            margin: 0;
        }}

        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #e4e4e7;
            background: #09090b;
            margin: 0;
            padding: 0;
        }}

        .page {{
            padding: 60px 56px;
        }}

        .org-name {{
            font-size: 10pt;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 3px;
            color: #a1a1aa;
            margin-bottom: 8px;
        }}

        .title {{
            font-size: 32pt;
            font-weight: 300;
            color: #fafafa;
            margin: 0 0 6px 0;
        }}

        .subtitle {{
            font-size: 12pt;
            color: #71717a;
            margin-bottom: 4px;
        }}

        .date {{
            font-size: 10pt;
            color: #52525b;
        }}

        .divider {{
            border: none;
            border-top: 1px solid #27272a;
            margin: 32px 0;
        }}

        .section-label {{
            font-size: 9pt;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #71717a;
            margin-bottom: 20px;
        }}

        .item {{
            margin-bottom: 24px;
        }}

        .item-row {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 4px;
        }}

        .item-name {{
            font-weight: 600;
            font-size: 12pt;
            color: #fafafa;
        }}

        .item-price {{
            font-weight: 400;
            font-size: 12pt;
            color: #e4e4e7;
            font-variant-numeric: tabular-nums;
        }}

        .item-description {{
            color: #a1a1aa;
            font-size: 10pt;
            margin: 0;
            line-height: 1.5;
        }}

        .total-section {{
            background: #18181b;
            border-radius: 12px;
            padding: 28px 32px;
            margin: 32px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .total-label {{
            font-size: 9pt;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #71717a;
        }}

        .total-value {{
            font-size: 28pt;
            font-weight: 300;
            color: #fafafa;
            font-variant-numeric: tabular-nums;
        }}

        .notes-section {{
            margin: 24px 0;
        }}

        .notes-label {{
            font-size: 9pt;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #71717a;
            margin-bottom: 8px;
        }}

        .notes-text {{
            color: #a1a1aa;
            font-size: 10pt;
            line-height: 1.5;
        }}

        .terms {{
            margin-top: 40px;
            padding-top: 24px;
            border-top: 1px solid #27272a;
            color: #52525b;
            font-size: 9pt;
            line-height: 1.6;
        }}

        .signature-area {{
            margin-top: 48px;
        }}

        .signature-label {{
            font-size: 9pt;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #71717a;
            margin-bottom: 4px;
        }}

        .signer-name {{
            font-size: 10pt;
            color: #a1a1aa;
            margin-bottom: 16px;
        }}

        .signature-box {{
            border: 1px solid #27272a;
            border-radius: 8px;
            height: 80px;
            background: #18181b;
        }}

        .footer {{
            margin-top: 48px;
            padding-top: 20px;
            border-top: 1px solid #27272a;
            font-size: 9pt;
            color: #3f3f46;
        }}
    </style>
</head>
<body>
    <div class="page">
        <div class="org-name">{org_name}</div>
        <div class="title">Proposal</div>
        <div class="subtitle">Prepared for {client_name} {"&middot; " + client_company if client_company else ""}</div>
        <div class="date">{proposal_date}</div>

        <hr class="divider">

        <div class="section-label">Scope of Work</div>
        {items_html}

        <div class="total-section">
            <div class="total-label">Total Investment</div>
            <div class="total-value">{formatted_total}</div>
        </div>

        {"<div class='notes-section'><div class='notes-label'>Notes</div><div class='notes-text'>" + notes + "</div></div>" if notes else ""}

        <div class="terms">
            By signing below, you agree to the scope of work and investment outlined in this proposal.
            Payment terms: 50% due upon signing, 50% due upon completion.
        </div>

        <div class="signature-area">
            <div class="signature-label">Signature</div>
            <div class="signer-name">{client_name}</div>
            <div class="signature-box"></div>
        </div>

        <div class="footer">
            <p>Thank you for your business.</p>
        </div>
    </div>
</body>
</html>
"""


def generate_signed_proposal_html(
    proposal: dict[str, Any],
    items: list[dict[str, Any]],
    org_name: str,
    signature_data: str,
    signed_at: str,
) -> str:
    """Generate HTML for the signed proposal PDF (server-side template)."""
    client_name = f"{proposal.get('client_name_f', '')} {proposal.get('client_name_l', '')}".strip()
    client_company = proposal.get("client_company") or ""
    total = float(proposal.get("total", 0))
    formatted_total = f"${total:,.0f}"
    notes = proposal.get("notes") or ""

    # Format signed date
    try:
        signed_date = datetime.fromisoformat(signed_at.replace("Z", "+00:00")).strftime("%B %d, %Y")
    except Exception:
        signed_date = signed_at

    # Build items HTML
    items_html = ""
    for item in items:
        item_name = item.get("name", "Project")
        item_desc = item.get("description", "")
        item_price = float(item.get("price", 0))
        items_html += f"""
        <div class="item">
            <div class="item-header">
                <span class="item-name">{item_name}</span>
                <span class="item-price">${item_price:,.0f}</span>
            </div>
            <p class="item-desc">{item_desc}</p>
        </div>
        """

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Proposal for {client_company or client_name} - Signed</title>
    <style>
        @page {{
            size: letter;
            margin: 0;
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #000;
            color: #fff;
            padding: 48px;
            font-size: 11pt;
            line-height: 1.5;
        }}
        .card {{
            background: #0a0a0a;
            border: 1px solid #1a1a1a;
            border-radius: 8px;
            overflow: hidden;
        }}
        .header {{
            padding: 40px 40px 32px 40px;
            border-bottom: 1px solid #1a1a1a;
        }}
        .org-name {{
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: rgba(255,255,255,0.4);
            margin-bottom: 24px;
        }}
        .title {{
            font-size: 28px;
            font-weight: 300;
            color: #fff;
            margin-bottom: 8px;
        }}
        .client-name {{
            color: rgba(255,255,255,0.5);
            font-size: 14px;
        }}
        .section {{
            padding: 32px 40px;
            border-bottom: 1px solid #1a1a1a;
        }}
        .section-label {{
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: rgba(255,255,255,0.4);
            margin-bottom: 20px;
        }}
        .item {{
            margin-bottom: 20px;
        }}
        .item:last-child {{
            margin-bottom: 0;
        }}
        .item-header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 4px;
        }}
        .item-name {{
            font-weight: 500;
            color: #fff;
        }}
        .item-price {{
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
            font-size: 12px;
            color: rgba(255,255,255,0.8);
        }}
        .item-desc {{
            font-size: 12px;
            color: rgba(255,255,255,0.5);
            line-height: 1.5;
        }}
        .total-section {{
            padding: 24px 40px;
            background: rgba(255,255,255,0.02);
        }}
        .total-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .total-label {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: rgba(255,255,255,0.4);
        }}
        .total-value {{
            font-size: 24px;
            font-weight: 300;
            color: #fff;
        }}
        .notes-section {{
            padding: 32px 40px;
            border-bottom: 1px solid #1a1a1a;
        }}
        .notes-text {{
            font-size: 12px;
            color: rgba(255,255,255,0.6);
            line-height: 1.6;
        }}
        .terms {{
            padding: 32px 40px;
            border-bottom: 1px solid #1a1a1a;
        }}
        .terms-text {{
            font-size: 11px;
            color: rgba(255,255,255,0.4);
            line-height: 1.6;
        }}
        .signed-section {{
            padding: 32px 40px;
            background: rgba(34, 197, 94, 0.05);
        }}
        .signed-badge {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .check-icon {{
            width: 20px;
            height: 20px;
            color: #22c55e;
        }}
        .signed-text {{
            color: #22c55e;
            font-size: 14px;
        }}
        .signature-image {{
            margin-top: 16px;
            max-height: 60px;
        }}
        .footer {{
            display: flex;
            justify-content: space-between;
            padding: 24px 8px;
            font-size: 11px;
            color: rgba(255,255,255,0.2);
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div class="org-name">{org_name}</div>
            <div class="title">Proposal for {client_company or client_name}</div>
            <div class="client-name">{client_name}</div>
        </div>

        <div class="section">
            <div class="section-label">Scope of Work</div>
            {items_html}
        </div>

        <div class="total-section">
            <div class="total-row">
                <span class="total-label">Total Investment</span>
                <span class="total-value">{formatted_total}</span>
            </div>
        </div>

        {"<div class='notes-section'><div class='section-label'>Notes</div><div class='notes-text'>" + notes + "</div></div>" if notes else ""}

        <div class="terms">
            <div class="terms-text">
                By signing below, you agree to the scope of work and investment outlined in this proposal and our Terms of Service.
            </div>
        </div>

        <div class="signed-section">
            <div class="signed-badge">
                <svg class="check-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                <span class="signed-text">Signed and accepted</span>
            </div>
            <img class="signature-image" src="{signature_data}" alt="Signature" />
        </div>
    </div>

    <div class="footer">
        <span>{signed_date}</span>
        <span>{org_name}</span>
    </div>
</body>
</html>"""


def wrap_signed_html_for_pdf(
    signed_html: str,
    signature_data: str,
    signer_name: str,
    signer_email: str | None,
    signed_at: str,
) -> str:
    """Wrap frontend-rendered proposal HTML with a signature page for PDF generation."""
    try:
        signed_date = datetime.fromisoformat(signed_at.replace("Z", "+00:00")).strftime("%B %d, %Y")
    except Exception:
        signed_date = signed_at

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Signed Proposal</title>
    <style>
        @page {{
            size: letter;
            margin: 0.75in;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.5;
            color: #111;
        }}
        .proposal-content {{
            margin-bottom: 0;
        }}
        .signature-page {{
            page-break-before: always;
            padding-top: 48px;
        }}
        .signature-page h2 {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 32px;
            color: #111;
        }}
        .sig-field {{
            margin-bottom: 16px;
        }}
        .sig-label {{
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: #888;
            margin-bottom: 4px;
        }}
        .sig-value {{
            font-size: 14px;
            color: #111;
        }}
        .sig-image {{
            margin: 24px 0;
            max-height: 80px;
        }}
        .sig-notice {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 11px;
            color: #888;
        }}
    </style>
</head>
<body>
    <div class="proposal-content">
        {signed_html}
    </div>

    <div class="signature-page">
        <h2>Signature</h2>

        <div class="sig-field">
            <div class="sig-label">Signed By</div>
            <div class="sig-value">{signer_name or "—"}</div>
        </div>

        {f'<div class="sig-field"><div class="sig-label">Email</div><div class="sig-value">{signer_email}</div></div>' if signer_email else ''}

        <div class="sig-field">
            <div class="sig-label">Date</div>
            <div class="sig-value">{signed_date}</div>
        </div>

        <img class="sig-image" src="{signature_data}" alt="Signature" />

        <div class="sig-notice">
            This document was electronically signed.
        </div>
    </div>
</body>
</html>"""


def generate_pdf_docraptor(html_content: str, filename: str) -> bytes:
    """Convert HTML to PDF using DocRaptor API."""
    import docraptor

    doc_api = docraptor.DocApi()
    doc_api.api_client.configuration.username = settings.DOCRAPTOR_API_KEY

    pdf_bytes = doc_api.create_doc({
        "test": False,  # Production mode - no watermark
        "document_type": "pdf",
        "document_content": html_content,
        "name": filename,
    })
    return pdf_bytes


def serialize_proposal_list_item(proposal: dict[str, Any]) -> ProposalListItem:
    """Serialize a proposal for list response (without items)."""
    status_id = proposal.get("status", 0)
    return ProposalListItem(
        id=proposal["id"],
        account_name=proposal.get("client_company"),
        contact_email=proposal["client_email"],
        contact_name=f"{proposal.get('client_name_f', '')} {proposal.get('client_name_l', '')}".strip(),
        contact_name_f=proposal.get("client_name_f", ""),
        contact_name_l=proposal.get("client_name_l", ""),
        status=PROPOSAL_STATUS_MAP.get(status_id, "Unknown"),
        status_id=status_id,
        total=format_currency(proposal.get("total")),
        notes=proposal.get("notes"),
        created_at=proposal["created_at"],
        updated_at=proposal["updated_at"],
        sent_at=proposal.get("sent_at"),
        signed_at=proposal.get("signed_at"),
        pdf_url=proposal.get("pdf_url"),
        converted_order_id=proposal.get("converted_order_id"),
        converted_engagement_id=proposal.get("converted_engagement_id"),
    )


def serialize_proposal_item(item: dict[str, Any]) -> ProposalItemResponse:
    """Serialize a proposal item."""
    return ProposalItemResponse(
        id=item["id"],
        name=item["name"],
        description=item.get("description"),
        price=format_currency(item.get("price")),
        service_id=item.get("service_id"),
        created_at=item["created_at"],
    )


def serialize_proposal(proposal: dict[str, Any], items: list[dict[str, Any]]) -> ProposalResponse:
    """Serialize a proposal with items."""
    status_id = proposal.get("status", 0)
    return ProposalResponse(
        id=proposal["id"],
        account_name=proposal.get("client_company"),
        contact_email=proposal["client_email"],
        contact_name=f"{proposal.get('client_name_f', '')} {proposal.get('client_name_l', '')}".strip(),
        contact_name_f=proposal.get("client_name_f", ""),
        contact_name_l=proposal.get("client_name_l", ""),
        status=PROPOSAL_STATUS_MAP.get(status_id, "Unknown"),
        status_id=status_id,
        total=format_currency(proposal.get("total")),
        notes=proposal.get("notes"),
        created_at=proposal["created_at"],
        updated_at=proposal["updated_at"],
        sent_at=proposal.get("sent_at"),
        signed_at=proposal.get("signed_at"),
        pdf_url=proposal.get("pdf_url"),
        converted_order_id=proposal.get("converted_order_id"),
        converted_engagement_id=proposal.get("converted_engagement_id"),
        items=[serialize_proposal_item(item) for item in items],
    )


def build_pagination_links(
    current_page: int, last_page: int, base_url: str, limit: int
) -> list[ProposalListMetaLink]:
    """Build pagination links for meta."""
    links: list[ProposalListMetaLink] = []

    # Previous link
    links.append(
        ProposalListMetaLink(
            url=f"{base_url}?page={current_page - 1}&limit={limit}" if current_page > 1 else None,
            label="Previous",
            active=False,
        )
    )

    # Page number links (up to 10)
    for i in range(1, min(last_page + 1, 11)):
        links.append(
            ProposalListMetaLink(
                url=f"{base_url}?page={i}&limit={limit}",
                label=str(i),
                active=i == current_page,
            )
        )

    # Next link
    links.append(
        ProposalListMetaLink(
            url=f"{base_url}?page={current_page + 1}&limit={limit}" if current_page < last_page else None,
            label="Next",
            active=False,
        )
    )

    return links


@router.get("", response_model=ProposalListResponse)
async def list_proposals(
    request: Request,
    auth: AuthContext = Depends(get_current_org),
    limit: int = Query(default=20, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    sort: str = Query(default="created_at:desc"),
) -> ProposalListResponse:
    """List proposals with pagination."""
    supabase = get_supabase()
    offset = (page - 1) * limit

    # Parse sort parameter
    sort_parts = sort.split(":")
    sort_field = sort_parts[0] if sort_parts else "created_at"
    sort_dir = sort_parts[1] if len(sort_parts) > 1 else "desc"

    valid_sort_fields = ["id", "client_email", "status", "total", "created_at", "sent_at", "signed_at"]
    if sort_field not in valid_sort_fields:
        sort_field = "created_at"
    ascending = sort_dir == "asc"

    # Get count
    count_result = supabase.table("proposals").select(
        "*", count="exact", head=True
    ).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

    total = count_result.count or 0

    # Get data
    query = supabase.table("proposals").select("*").eq(
        "org_id", auth.org_id
    ).is_("deleted_at", "null").order(
        sort_field, desc=not ascending
    ).range(offset, offset + limit - 1)

    # Apply filters from query params
    params = dict(request.query_params)
    filterable_fields = ["id", "status", "client_email", "created_at"]

    for key, value in params.items():
        # Parse filter format: filters[field][$op]
        if key.startswith("filters["):
            import re
            match = re.match(r"filters\[(\w+)\]\[(\$\w+)\]", key)
            if match:
                field, operator = match.groups()
                if field not in filterable_fields:
                    continue

                if operator == "$eq":
                    query = query.eq(field, value)
                elif operator == "$lt":
                    query = query.lt(field, value)
                elif operator == "$gt":
                    query = query.gt(field, value)

    result = await query.execute()
    proposals = result.data or []

    # Build response
    last_page = max(1, (total + limit - 1) // limit)
    base_url = str(request.url).split("?")[0]

    return ProposalListResponse(
        data=[serialize_proposal_list_item(p) for p in proposals],
        links=ProposalListLinks(
            first=f"{base_url}?page=1&limit={limit}",
            last=f"{base_url}?page={last_page}&limit={limit}",
            prev=f"{base_url}?page={page - 1}&limit={limit}" if page > 1 else None,
            next=f"{base_url}?page={page + 1}&limit={limit}" if page < last_page else None,
        ),
        meta=ProposalListMeta(
            current_page=page,
            from_=offset + 1 if total > 0 else 0,
            to=min(offset + limit, total),
            last_page=last_page,
            per_page=limit,
            total=total,
            path=base_url,
            links=build_pagination_links(page, last_page, base_url, limit),
        ),
    )


@router.post("", response_model=ProposalResponse, status_code=201)
async def create_proposal(
    body: CreateProposalRequest,
    auth: AuthContext = Depends(get_current_org),
) -> ProposalResponse:
    """Create a new proposal."""
    supabase = get_supabase()

    # Validate service_ids if provided (optional template references)
    service_ids = [item.service_id for item in body.items if item.service_id]
    if service_ids:
        services_result = supabase.table("services").select("id").eq(
            "org_id", auth.org_id
        ).is_("deleted_at", "null").in_("id", service_ids).execute()

        found_service_ids = {s["id"] for s in (services_result.data or [])}
        missing_services = [sid for sid in service_ids if sid not in found_service_ids]

        if missing_services:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "The given data was invalid.",
                    "errors": {"items": [f"Service with ID {missing_services[0]} does not exist."]},
                },
            )

    # Calculate total from item prices
    total = sum(item.price for item in body.items)

    # Get org details for email
    org_result = supabase.table("organizations").select("name, domain, notification_email").eq("id", auth.org_id).execute()
    org = org_result.data[0] if org_result.data else {}
    org_name = org.get("name", "Service Engine X")
    from_email = org.get("notification_email") or f"proposals@{org.get('domain', 'serviceengine.xyz')}"

    now = datetime.now(timezone.utc).isoformat()

    # Create proposal (map account/contact fields to database columns)
    proposal_data = {
        "org_id": auth.org_id,
        "client_email": body.contact_email.lower().strip(),
        "client_name_f": body.contact_name_f.strip(),
        "client_name_l": body.contact_name_l.strip(),
        "client_company": body.account_name,
        "status": 1,  # Sent
        "sent_at": now,
        "total": total,
        "notes": body.notes,
    }

    proposal_result = supabase.table("proposals").insert(proposal_data).execute()

    if not proposal_result.data:
        raise HTTPException(status_code=500, detail="Failed to create proposal")

    proposal_id = proposal_result.data[0]["id"]

    # Fetch full proposal record
    proposal_fetch = supabase.table("proposals").select("*").eq("id", proposal_id).execute()
    proposal = proposal_fetch.data[0]

    # Create proposal items (each defines a project)
    item_rows = [
        {
            "proposal_id": proposal_id,
            "name": item.name,
            "description": item.description,
            "price": item.price,
            "service_id": item.service_id,
        }
        for item in body.items
    ]

    items_result = supabase.table("proposal_items").insert(item_rows).execute()

    # Fetch full items
    items_fetch = supabase.table("proposal_items").select("*").eq("proposal_id", proposal_id).execute()

    if not items_fetch.data:
        # Clean up proposal if items failed
        supabase.table("proposals").delete().eq("id", proposal["id"]).execute()
        raise HTTPException(status_code=500, detail="Failed to create proposal items")

    # Send proposal email
    contact_name = f"{body.contact_name_f} {body.contact_name_l}".strip()
    signing_url = f"https://revenueactivation.com/p/{proposal_id}"
    formatted_total = f"${total:,.0f}"

    try:
        send_proposal_email(
            to_email=body.contact_email.lower().strip(),
            from_email=from_email,
            contact_name=contact_name,
            org_name=org_name,
            signing_url=signing_url,
            total=formatted_total,
            subject=body.email_subject,
            body=body.email_body,
        )
    except Exception as e:
        print(f"Failed to send proposal email: {e}")

    return serialize_proposal(proposal, items_fetch.data)


@router.get("/{proposal_id}", response_model=ProposalResponse)
async def retrieve_proposal(
    proposal_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> ProposalResponse:
    """Retrieve a proposal by ID."""
    supabase = get_supabase()

    # Fetch proposal with items
    result = supabase.table("proposals").select(
        "*, proposal_items (*)"
    ).eq("id", proposal_id).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Not Found")

    proposal = result.data[0]
    items = proposal.get("proposal_items") or []

    return serialize_proposal(proposal, items)


@router.get("/{proposal_id}/deliverables")
async def get_proposal_deliverables(
    proposal_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> dict[str, Any]:
    """
    Get what was purchased from a signed proposal.

    Returns the projects (deliverables) created from this proposal,
    with their linked service details. Only works for signed proposals.

    Response includes:
    - proposal: Basic proposal info
    - engagement: The engagement container
    - projects: List of projects with service details
    - order: Financial record
    """
    supabase = get_supabase()

    # Fetch proposal
    result = supabase.table("proposals").select(
        "*, proposal_items (*)"
    ).eq("id", proposal_id).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Not Found")

    proposal = result.data[0]
    items = proposal.get("proposal_items") or []

    # Must be signed
    if proposal["status"] != 2:
        raise HTTPException(
            status_code=400,
            detail="Proposal is not signed. Deliverables are only available after signing.",
        )

    engagement_id = proposal.get("converted_engagement_id")
    order_id = proposal.get("converted_order_id")

    if not engagement_id:
        raise HTTPException(
            status_code=500,
            detail="Signed proposal is missing engagement reference.",
        )

    # Fetch engagement
    engagement_result = supabase.table("engagements").select("*").eq(
        "id", engagement_id
    ).execute()

    engagement = engagement_result.data[0] if engagement_result.data else None

    # Fetch projects with service details
    projects_result = supabase.table("projects").select(
        "*, services:service_id (id, name, description, price, recurring)"
    ).eq("engagement_id", engagement_id).is_("deleted_at", "null").order(
        "created_at", desc=False
    ).execute()

    projects = projects_result.data or []

    # Fetch order if exists
    order = None
    if order_id:
        order_result = supabase.table("orders").select("*").eq("id", order_id).execute()
        if order_result.data:
            order = order_result.data[0]

    # Build response
    client_name = f"{proposal.get('client_name_f', '')} {proposal.get('client_name_l', '')}".strip()

    return {
        "proposal": {
            "id": proposal["id"],
            "account_name": proposal.get("client_company"),
            "contact_name": client_name,
            "contact_email": proposal.get("client_email"),
            "total": format_currency(proposal.get("total")),
            "signed_at": proposal.get("signed_at"),
            "notes": proposal.get("notes"),
        },
        "engagement": {
            "id": engagement["id"],
            "name": engagement["name"],
            "status": "Active" if engagement["status"] == 1 else "Paused" if engagement["status"] == 2 else "Closed",
            "status_id": engagement["status"],
            "created_at": engagement["created_at"],
        } if engagement else None,
        "projects": [
            {
                "id": p["id"],
                "name": p["name"],
                "description": p.get("description"),
                "status": "Active" if p["status"] == 1 else "Paused" if p["status"] == 2 else "Completed" if p["status"] == 3 else "Cancelled",
                "status_id": p["status"],
                "phase": {1: "Kickoff", 2: "Setup", 3: "Build", 4: "Testing", 5: "Deployment", 6: "Handoff"}.get(p.get("phase", 1), "Kickoff"),
                "phase_id": p.get("phase", 1),
                "service": {
                    "id": p["services"]["id"],
                    "name": p["services"]["name"],
                    "description": p["services"].get("description"),
                    "price": format_currency(p["services"].get("price")),
                    "recurring": p["services"].get("recurring", 0),
                } if p.get("services") else None,
                "created_at": p["created_at"],
            }
            for p in projects
        ],
        "order": {
            "id": order["id"],
            "number": order["number"],
            "price": format_currency(order.get("price")),
            "currency": order.get("currency", "USD"),
            "status": ORDER_STATUS_MAP.get(order.get("status", 0), "Unknown"),
            "status_id": order.get("status", 0),
            "paid_at": order.get("paid_at"),
            "created_at": order["created_at"],
        } if order else None,
    }


@router.post("/{proposal_id}/send", response_model=ProposalResponse)
async def send_proposal(
    proposal_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> ProposalResponse:
    """
    Send a proposal (Draft -> Sent).

    This endpoint:
    1. Generates a PDF of the proposal using DocRaptor
    2. Stores the PDF in Supabase Storage
    3. Updates status to Sent
    """
    supabase = get_supabase()

    # Fetch proposal with items
    result = supabase.table("proposals").select(
        "*, proposal_items (*)"
    ).eq("id", proposal_id).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Not Found")

    proposal = result.data[0]
    items = proposal.get("proposal_items") or []

    # Check if proposal can be sent (must be Draft)
    if proposal["status"] != 0:
        status_name = PROPOSAL_STATUS_MAP.get(proposal["status"], "Unknown")
        raise HTTPException(
            status_code=400,
            detail=f"Cannot send proposal with status {status_name}",
        )

    # Get org name for branding
    org_result = supabase.table("organizations").select("name").eq("id", auth.org_id).execute()
    org_name = org_result.data[0]["name"] if org_result.data else "Service Engine X"

    # Generate HTML
    html_content = generate_proposal_html(proposal, items, org_name)

    # Convert to PDF via DocRaptor
    client_name = f"{proposal.get('client_name_f', '')} {proposal.get('client_name_l', '')}".strip()
    filename = f"proposal-{proposal_id[:8]}.pdf"

    try:
        pdf_bytes = generate_pdf_docraptor(html_content, filename)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF: {str(e)}",
        )

    # Store PDF in Supabase Storage (self-hosted)
    try:
        pdf_url = upload_proposal_pdf(auth.org_id, proposal_id, pdf_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store PDF: {str(e)}",
        )

    # Update proposal with PDF URL and status
    now = datetime.now(timezone.utc).isoformat()

    supabase.table("proposals").update({
        "status": 1,
        "sent_at": now,
        "updated_at": now,
        "pdf_url": pdf_url,
    }).eq("id", proposal_id).execute()

    # Update local proposal dict for response
    proposal["status"] = 1
    proposal["sent_at"] = now
    proposal["updated_at"] = now
    proposal["pdf_url"] = pdf_url

    return serialize_proposal(proposal, items)


@router.post("/{proposal_id}/sign")
async def sign_proposal(
    proposal_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> dict[str, Any]:
    """
    Sign a proposal (Sent -> Signed).

    Creates:
    - An engagement (work relationship container)
    - Projects for each proposal item
    - An order (financial transaction record)
    """
    supabase = get_supabase()

    # Fetch proposal with items
    result = supabase.table("proposals").select(
        "*, proposal_items (*)"
    ).eq("id", proposal_id).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Not Found")

    proposal = result.data[0]

    # Check if proposal can be signed (must be Sent)
    if proposal["status"] != 1:
        status_name = PROPOSAL_STATUS_MAP.get(proposal["status"], "Unknown")
        raise HTTPException(
            status_code=400,
            detail=f"Cannot sign proposal with status {status_name}",
        )

    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    items = proposal.get("proposal_items") or []

    # Find or create client user
    client_id: str | None = None

    existing_user_result = supabase.table("users").select("id").eq(
        "email", proposal["client_email"]
    ).eq("org_id", auth.org_id).execute()

    if existing_user_result.data:
        client_id = existing_user_result.data[0]["id"]
    else:
        # Get client role (dashboard_access = 0)
        role_result = supabase.table("roles").select("id").eq(
            "dashboard_access", 0
        ).execute()

        if role_result.data:
            # Create new user
            new_user_result = supabase.table("users").insert({
                "org_id": auth.org_id,
                "email": proposal["client_email"],
                "name_f": proposal["client_name_f"],
                "name_l": proposal["client_name_l"],
                "company": proposal.get("client_company"),
                "role_id": role_result.data[0]["id"],
                "status": 1,
                "balance": "0.00",
                "spent": "0.00",
                "custom_fields": {},
            }).execute()

            if new_user_result.data:
                client_id = new_user_result.data[0]["id"]

    # =========================================================================
    # CREATE ENGAGEMENT (work relationship container)
    # =========================================================================
    client_name = f"{proposal['client_name_f']} {proposal['client_name_l']}".strip()
    engagement_name = f"{client_name} - {proposal.get('notes', 'Engagement')[:50] if proposal.get('notes') else 'New Engagement'}"

    engagement_data = {
        "org_id": auth.org_id,
        "client_id": client_id,
        "name": engagement_name,
        "status": 1,  # Active
        "proposal_id": proposal_id,
        "created_at": now,
        "updated_at": now,
    }

    engagement_result = supabase.table("engagements").insert(engagement_data).execute()

    if not engagement_result.data:
        raise HTTPException(status_code=500, detail="Failed to create engagement")

    engagement = engagement_result.data[0]

    # =========================================================================
    # CREATE PROJECTS (one per proposal item)
    # =========================================================================
    projects_created = []

    for item in items:
        project_data = {
            "engagement_id": engagement["id"],
            "org_id": auth.org_id,
            "name": item["name"],
            "description": item.get("description"),
            "status": 1,  # Active
            "phase": 1,   # Kickoff
            "service_id": item.get("service_id"),  # Optional template reference
            "created_at": now,
            "updated_at": now,
        }

        project_result = supabase.table("projects").insert(project_data).execute()

        if project_result.data:
            projects_created.append(project_result.data[0])

    # =========================================================================
    # CREATE ORDER (financial transaction record)
    # =========================================================================
    primary_item = items[0] if items else None

    # Use primary item name or fallback
    order_name = primary_item["name"] if primary_item else "Proposal Order"

    order_data = {
        "org_id": auth.org_id,
        "number": generate_order_number(),
        "user_id": client_id,
        "service_id": primary_item.get("service_id") if primary_item else None,
        "service_name": order_name,
        "price": proposal["total"],
        "currency": "USD",
        "quantity": 1,
        "status": 0,  # Unpaid
        "engagement_id": engagement["id"],  # Link to engagement
        "note": f"Created from proposal. {proposal.get('notes') or ''}".strip(),
        "form_data": {},
        "metadata": {
            "proposal_id": proposal["id"],
            "engagement_id": engagement["id"],
            "proposal_items": [
                {
                    "name": item["name"],
                    "description": item.get("description"),
                    "price": str(item["price"]),
                    "service_id": item.get("service_id"),
                }
                for item in items
            ],
        },
    }

    order_result = supabase.table("orders").insert(order_data).execute()

    if not order_result.data:
        raise HTTPException(status_code=500, detail="Failed to create order")

    order = order_result.data[0]

    # =========================================================================
    # UPDATE PROPOSAL
    # =========================================================================
    supabase.table("proposals").update({
        "status": 2,
        "signed_at": now,
        "updated_at": now,
        "converted_order_id": order["id"],
        "converted_engagement_id": engagement["id"],
    }).eq("id", proposal_id).execute()

    # Update local proposal dict for response
    proposal["status"] = 2
    proposal["signed_at"] = now
    proposal["updated_at"] = now
    proposal["converted_order_id"] = order["id"]
    proposal["converted_engagement_id"] = engagement["id"]

    # =========================================================================
    # BUILD RESPONSE
    # =========================================================================
    proposal_response = serialize_proposal(proposal, items)

    order_response = {
        "id": order["id"],
        "number": order["number"],
        "user_id": order["user_id"],
        "service_id": order["service_id"],
        "service": order["service_name"],
        "price": str(order["price"]),
        "currency": order["currency"],
        "quantity": order["quantity"],
        "status": ORDER_STATUS_MAP.get(order["status"], "Unknown"),
        "status_id": order["status"],
        "engagement_id": order["engagement_id"],
        "note": order["note"],
        "created_at": order["created_at"],
    }

    engagement_response = {
        "id": engagement["id"],
        "client_id": engagement["client_id"],
        "name": engagement["name"],
        "status": "Active",
        "status_id": 1,
        "created_at": engagement["created_at"],
    }

    projects_response = [
        {
            "id": p["id"],
            "name": p["name"],
            "status": "Active",
            "status_id": 1,
            "phase": "Kickoff",
            "phase_id": 1,
            "service_id": p.get("service_id"),
        }
        for p in projects_created
    ]

    return {
        "proposal": proposal_response.model_dump(),
        "engagement": engagement_response,
        "projects": projects_response,
        "order": order_response,
    }


# =============================================================================
# PUBLIC ENDPOINTS (No auth required - for client-facing proposal pages)
# =============================================================================

# Create a separate router for public endpoints
public_router = APIRouter(prefix="/api/public/proposals", tags=["Public Proposals"])


def _resolve_public_proposal(
    supabase: Any,
    proposal_id: str,
    select_fields: str,
) -> dict[str, Any]:
    """
    Resolve a public proposal identifier to a proposal row.

    Supports:
    - Short ID: first 1-8 hex chars of UUID
    - Full UUID
    """
    import re

    if len(proposal_id) <= 8:
        if not re.fullmatch(r"[0-9a-fA-F]{1,8}", proposal_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid proposal_id. Use a UUID or 1-8 hex characters.",
            )

        prefix_value = int(proposal_id, 16)
        lower_prefix = f"{prefix_value:08x}"
        uuid_lower = f"{lower_prefix}-0000-0000-0000-000000000000"

        query = supabase.table("proposals").select(select_fields).gte("id", uuid_lower)
        if prefix_value < 0xFFFFFFFF:
            upper_prefix = f"{prefix_value + 1:08x}"
            uuid_upper = f"{upper_prefix}-0000-0000-0000-000000000000"
            query = query.lt("id", uuid_upper)

        result = query.is_("deleted_at", "null").execute()
    else:
        try:
            normalized_uuid = str(UUID(proposal_id))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid proposal_id. Use a UUID or 1-8 hex characters.",
            ) from None

        result = (
            supabase.table("proposals")
            .select(select_fields)
            .eq("id", normalized_uuid)
            .is_("deleted_at", "null")
            .execute()
        )

    if not result.data:
        raise HTTPException(status_code=404, detail="Proposal not found")

    return result.data[0]


@public_router.get("/{proposal_id}")
async def get_public_proposal(proposal_id: str) -> dict[str, Any]:
    """
    Get proposal data for public viewing/signing.
    No authentication required - used by client-facing proposal pages.

    Accepts either a full UUID or the first 8 characters as a short ID.
    Returns proposal details and PDF URL for the public proposal page.
    """
    supabase = get_supabase()

    proposal = _resolve_public_proposal(
        supabase=supabase,
        proposal_id=proposal_id,
        select_fields="*, proposal_items (*), organizations:org_id (name, slug, domain, stripe_publishable_key)",
    )

    # Only allow viewing if proposal has been sent
    if proposal["status"] < 1:
        raise HTTPException(status_code=404, detail="Proposal not found")

    items = proposal.get("proposal_items") or []
    org = proposal.get("organizations") or {}

    # Check if already signed
    is_signed = proposal["status"] == 2

    # Fetch tenant org's bank details
    bank_result = (
        supabase.table("organization_bank_details")
        .select("*")
        .eq("org_id", proposal["org_id"])
        .execute()
    )
    bank_row = bank_result.data[0] if bank_result.data else None
    bank_details = None
    if bank_row:
        bank_details = {
            "account_name": bank_row["account_name"],
            "account_number": bank_row.get("account_number"),
            "routing_number": bank_row.get("routing_number"),
            "bank_name": bank_row.get("bank_name"),
            "bank_address_line1": bank_row.get("bank_address_line1"),
            "bank_address_line2": bank_row.get("bank_address_line2"),
            "bank_city": bank_row.get("bank_city"),
            "bank_state": bank_row.get("bank_state"),
            "bank_postal_code": bank_row.get("bank_postal_code"),
            "bank_country": bank_row.get("bank_country"),
            "swift_code": bank_row.get("swift_code"),
            "iban": bank_row.get("iban"),
        }

    return {
        "id": proposal["id"],
        "org_name": org.get("name", ""),
        "org_slug": org.get("slug", ""),
        "org_domain": org.get("domain", ""),
        "stripe_publishable_key": org.get("stripe_publishable_key"),
        "contact_name": f"{proposal.get('client_name_f', '')} {proposal.get('client_name_l', '')}".strip(),
        "account_name": proposal.get("client_company"),
        "contact_email": proposal.get("client_email"),
        "status": PROPOSAL_STATUS_MAP.get(proposal["status"], "Unknown"),
        "status_id": proposal["status"],
        "total": format_currency(proposal.get("total")),
        "notes": proposal.get("notes"),
        "sent_at": proposal.get("sent_at"),
        "signed_at": proposal.get("signed_at"),
        "is_signed": is_signed,
        "pdf_url": proposal.get("pdf_url"),
        "bank_details": bank_details,
        "items": [
            {
                "id": item["id"],
                "name": item["name"],
                "description": item.get("description"),
                "price": format_currency(item.get("price")),
            }
            for item in items
        ],
    }


@public_router.post("/{proposal_id}/checkout")
async def public_create_checkout(proposal_id: str) -> dict[str, Any]:
    """
    Create a Stripe Checkout session for a proposal.

    No authentication required. Looks up the proposal and org's Stripe key,
    builds line items from proposal_items, and returns a checkout URL.
    """
    supabase = get_supabase()

    proposal = _resolve_public_proposal(
        supabase=supabase,
        proposal_id=proposal_id,
        select_fields="*, proposal_items (*), organizations:org_id (stripe_secret_key, domain)",
    )
    items = proposal.get("proposal_items") or []
    org = proposal.get("organizations") or {}

    stripe_key = org.get("stripe_secret_key")
    org_domain = org.get("domain")

    if not stripe_key:
        raise HTTPException(status_code=400, detail="Organization has no Stripe key configured")

    if not items:
        raise HTTPException(status_code=400, detail="Proposal has no items")

    # Build Stripe line items from proposal items
    stripe_line_items = build_line_items_from_proposal(items)

    # Build redirect URLs
    success_url = f"https://{org_domain}?payment=success&proposal_id={proposal_id}" if org_domain else f"https://example.com?payment=success&proposal_id={proposal_id}"
    cancel_url = f"https://{org_domain}?payment=cancelled&proposal_id={proposal_id}" if org_domain else f"https://example.com?payment=cancelled&proposal_id={proposal_id}"

    checkout_result = create_checkout_session(
        api_key=stripe_key,
        line_items=stripe_line_items,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "org_id": proposal["org_id"],
            "proposal_id": proposal["id"],
        },
        customer_email=proposal.get("client_email"),
    )

    return {
        "checkout_url": checkout_result["checkout_url"],
        "session_id": checkout_result["session_id"],
    }


@public_router.post("/{proposal_id}/payment-intent")
async def public_create_payment_intent(proposal_id: str) -> dict[str, Any]:
    """
    Create a Stripe PaymentIntent for a proposal (for use with Stripe Elements).

    No authentication required. Returns the client_secret for the frontend
    to confirm payment via stripe.confirmPayment().
    """
    import stripe as stripe_lib

    supabase = get_supabase()

    proposal = _resolve_public_proposal(
        supabase=supabase,
        proposal_id=proposal_id,
        select_fields="*, proposal_items (*), organizations:org_id (stripe_secret_key)",
    )
    items = proposal.get("proposal_items") or []
    org = proposal.get("organizations") or {}

    stripe_key = org.get("stripe_secret_key")
    if not stripe_key:
        raise HTTPException(status_code=400, detail="Organization has no Stripe key configured")

    if not items:
        raise HTTPException(status_code=400, detail="Proposal has no items")

    # Calculate total in cents
    total_cents = sum(int(float(item.get("price", 0)) * 100) for item in items)

    if total_cents <= 0:
        raise HTTPException(status_code=400, detail="Proposal total must be greater than zero")

    stripe_lib.api_key = stripe_key

    intent = stripe_lib.PaymentIntent.create(
        amount=total_cents,
        currency="usd",
        metadata={
            "org_id": proposal["org_id"],
            "proposal_id": proposal["id"],
        },
        receipt_email=proposal.get("client_email"),
    )

    return {
        "client_secret": intent.client_secret,
        "payment_intent_id": intent.id,
        "amount": total_cents,
    }


@public_router.get("/{proposal_id}/signed-pdf")
async def get_signed_pdf(proposal_id: str):
    """
    Download the signed PDF for a proposal.

    No authentication required — public endpoint (same access model as viewing a proposal).
    Redirects to the Supabase Storage URL for the signed PDF.
    """
    supabase = get_supabase()

    proposal = _resolve_public_proposal(
        supabase=supabase,
        proposal_id=proposal_id,
        select_fields="id, status",
    )

    if proposal["status"] != 2:
        raise HTTPException(status_code=404, detail="Signed PDF not available")

    # Look up the signature record for the PDF URL
    sig_result = (
        supabase.table("proposal_signatures")
        .select("signed_pdf_url")
        .eq("proposal_id", proposal["id"])
        .execute()
    )

    if not sig_result.data or not sig_result.data[0].get("signed_pdf_url"):
        raise HTTPException(status_code=404, detail="Signed PDF not found")

    return RedirectResponse(url=sig_result.data[0]["signed_pdf_url"])


@public_router.post("/{proposal_id}/sign")
async def public_sign_proposal(proposal_id: str, request: Request) -> dict[str, Any]:
    """
    Sign a proposal from the public proposal page.

    No authentication required — the client signs from the public link.
    Records signature data, timestamp, IP, and user agent for legal proof.
    Creates engagement, projects, and order on successful signing.

    Request body:
        signed_html: full rendered HTML of the proposal page as the signer saw it
        signature: base64-encoded signature image (PNG data URL)
        signer_name: full name of the signer
        signer_email: signer's email address
    """
    supabase = get_supabase()

    # Parse request body
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request body")

    signed_html = body.get("signed_html")
    signature_data = body.get("signature")
    signer_name = body.get("signer_name")
    signer_email = body.get("signer_email")

    if not signature_data:
        raise HTTPException(status_code=400, detail="Signature is required")
    if not signed_html:
        raise HTTPException(status_code=400, detail="signed_html is required")

    proposal = _resolve_public_proposal(
        supabase=supabase,
        proposal_id=proposal_id,
        select_fields="*, proposal_items (*), organizations:org_id (name, slug, domain, stripe_publishable_key)",
    )
    full_proposal_id = proposal["id"]
    org_id = proposal["org_id"]
    org = proposal.get("organizations") or {}
    org_name = org.get("name", "Service Engine X")

    # Must be in Sent status
    if proposal["status"] != 1:
        status_name = PROPOSAL_STATUS_MAP.get(proposal["status"], "Unknown")
        raise HTTPException(
            status_code=400,
            detail=f"Cannot sign proposal with status {status_name}",
        )

    now = datetime.now(timezone.utc).isoformat()
    items = proposal.get("proposal_items") or []

    # Capture signer metadata
    signer_ip = None
    if request.client:
        signer_ip = request.client.host
    # Check for forwarded IP (behind proxy/load balancer)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        signer_ip = forwarded_for.split(",")[0].strip()

    signer_user_agent = request.headers.get("user-agent", "")

    # =========================================================================
    # FIND OR CREATE ACCOUNT + CONTACT (NEW CRM MODEL)
    # =========================================================================
    account_id: str | None = None
    contact_id: str | None = None
    client_email = proposal["client_email"]
    company_name = proposal.get("client_company")

    # Extract domain from email for account matching
    email_domain = client_email.split("@")[1].lower() if "@" in client_email else None

    # Try to find existing account by company name or email domain
    if company_name:
        existing_account = supabase.table("accounts").select("id").eq(
            "org_id", org_id
        ).eq("name", company_name).is_("deleted_at", "null").execute()
        if existing_account.data:
            account_id = existing_account.data[0]["id"]

    if not account_id and email_domain:
        # Try matching by domain (excluding common email providers)
        common_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com", "aol.com"]
        if email_domain not in common_domains:
            existing_account = supabase.table("accounts").select("id").eq(
                "org_id", org_id
            ).eq("domain", email_domain).is_("deleted_at", "null").execute()
            if existing_account.data:
                account_id = existing_account.data[0]["id"]

    # Create account if not found
    if not account_id:
        account_name = company_name or f"{proposal['client_name_f']} {proposal['client_name_l']}".strip()
        account_data = {
            "org_id": org_id,
            "name": account_name,
            "domain": email_domain if email_domain and email_domain not in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com", "aol.com"] else None,
            "lifecycle": "active",  # Signed proposal = active account
            "source": "proposal",
            "balance": 0.00,
            "total_spent": 0.00,
            "created_at": now,
            "updated_at": now,
        }
        account_result = supabase.table("accounts").insert(account_data).execute()
        if account_result.data:
            account_id = account_result.data[0]["id"]
    else:
        # Update existing account lifecycle to active
        supabase.table("accounts").update({
            "lifecycle": "active",
            "updated_at": now,
        }).eq("id", account_id).execute()

    # Find or create contact
    existing_contact = supabase.table("contacts").select("id, user_id").eq(
        "org_id", org_id
    ).eq("email", client_email).is_("deleted_at", "null").execute()

    if existing_contact.data:
        contact_id = existing_contact.data[0]["id"]
        # Link to account if not already linked
        if account_id:
            supabase.table("contacts").update({
                "account_id": account_id,
                "updated_at": now,
            }).eq("id", contact_id).execute()
    else:
        contact_data = {
            "org_id": org_id,
            "account_id": account_id,
            "name_f": proposal["client_name_f"],
            "name_l": proposal["client_name_l"],
            "email": client_email,
            "is_primary": True,
            "is_billing": True,
            "created_at": now,
            "updated_at": now,
        }
        contact_result = supabase.table("contacts").insert(contact_data).execute()
        if contact_result.data:
            contact_id = contact_result.data[0]["id"]

    # =========================================================================
    # FIND OR CREATE CLIENT USER (LEGACY - FOR PORTAL ACCESS)
    # =========================================================================
    client_id: str | None = None

    existing_user_result = supabase.table("users").select("id").eq(
        "email", proposal["client_email"]
    ).eq("org_id", org_id).execute()

    if existing_user_result.data:
        client_id = existing_user_result.data[0]["id"]
    else:
        role_result = supabase.table("roles").select("id").eq(
            "dashboard_access", 0
        ).execute()

        if role_result.data:
            new_user_result = supabase.table("users").insert({
                "org_id": org_id,
                "email": proposal["client_email"],
                "name_f": proposal["client_name_f"],
                "name_l": proposal["client_name_l"],
                "company": proposal.get("client_company"),
                "role_id": role_result.data[0]["id"],
                "status": 1,
                "balance": "0.00",
                "spent": "0.00",
                "custom_fields": {},
                "password_hash": "unsigned",
            }).execute()

            if new_user_result.data:
                client_id = new_user_result.data[0]["id"]

    # Link contact to user if both exist
    if contact_id and client_id:
        supabase.table("contacts").update({
            "user_id": client_id,
            "updated_at": now,
        }).eq("id", contact_id).execute()

    # =========================================================================
    # CREATE ENGAGEMENT (WITH BOTH client_id AND account_id)
    # =========================================================================
    client_name = f"{proposal['client_name_f']} {proposal['client_name_l']}".strip()
    engagement_name = f"{client_name} - {proposal.get('notes', 'Engagement')[:50] if proposal.get('notes') else 'New Engagement'}"

    engagement_result = supabase.table("engagements").insert({
        "org_id": org_id,
        "client_id": client_id,
        "account_id": account_id,  # NEW: Link to account
        "name": engagement_name,
        "status": 1,
        "proposal_id": full_proposal_id,
        "created_at": now,
        "updated_at": now,
    }).execute()

    if not engagement_result.data:
        raise HTTPException(status_code=500, detail="Failed to create engagement")

    engagement = engagement_result.data[0]

    # =========================================================================
    # CREATE PROJECTS (one per proposal item)
    # =========================================================================
    projects_created = []
    for item in items:
        project_result = supabase.table("projects").insert({
            "engagement_id": engagement["id"],
            "org_id": org_id,
            "name": item["name"],
            "description": item.get("description"),
            "status": 1,
            "phase": 1,
            "service_id": item.get("service_id"),
            "created_at": now,
            "updated_at": now,
        }).execute()

        if project_result.data:
            projects_created.append(project_result.data[0])

    # =========================================================================
    # CREATE ORDER
    # =========================================================================
    primary_item = items[0] if items else None
    order_name = primary_item["name"] if primary_item else "Proposal Order"

    order_result = supabase.table("orders").insert({
        "org_id": org_id,
        "number": generate_order_number(),
        "user_id": client_id,
        "account_id": account_id,  # NEW: Link to account
        "service_id": primary_item.get("service_id") if primary_item else None,
        "service_name": order_name,
        "price": proposal["total"],
        "currency": "USD",
        "quantity": 1,
        "status": 0,
        "engagement_id": engagement["id"],
        "note": f"Created from proposal. {proposal.get('notes') or ''}".strip(),
        "form_data": {},
        "metadata": {
            "proposal_id": full_proposal_id,
            "engagement_id": engagement["id"],
            "account_id": account_id,
            "contact_id": contact_id,
            "signer_name": signer_name,
            "signer_ip": signer_ip,
            "signed_at": now,
        },
    }).execute()

    if not order_result.data:
        raise HTTPException(status_code=500, detail="Failed to create order")

    order = order_result.data[0]

    # =========================================================================
    # CREATE STRIPE CHECKOUT SESSION
    # =========================================================================
    checkout_url: str | None = None

    # Fetch org's Stripe config
    org_result = supabase.table("organizations").select(
        "stripe_secret_key, domain"
    ).eq("id", org_id).execute()

    if org_result.data:
        org_data = org_result.data[0]
        stripe_key = org_data.get("stripe_secret_key")
        org_domain = org_data.get("domain")

        if stripe_key and org_domain:
            try:
                # Build line items from proposal items
                stripe_line_items = build_line_items_from_proposal(items)

                # Create checkout session
                success_url = f"https://{org_domain}?payment=success&order_id={order['id']}"
                cancel_url = f"https://{org_domain}?payment=cancelled&proposal_id={full_proposal_id}"

                checkout_result = create_checkout_session(
                    api_key=stripe_key,
                    line_items=stripe_line_items,
                    success_url=success_url,
                    cancel_url=cancel_url,
                    metadata={
                        "org_id": org_id,
                        "proposal_id": full_proposal_id,
                        "order_id": order["id"],
                        "engagement_id": engagement["id"],
                    },
                    customer_email=proposal.get("client_email"),
                )

                checkout_url = checkout_result["checkout_url"]
                session_id = checkout_result["session_id"]

                # Update order with Stripe session ID
                supabase.table("orders").update({
                    "stripe_checkout_session_id": session_id,
                }).eq("id", order["id"]).execute()

            except Exception:
                # Stripe failure is non-blocking — signing still succeeds
                pass

    # =========================================================================
    # UPDATE PROPOSAL — mark as signed with signature proof
    # =========================================================================

    # Generate signed PDF from frontend HTML + signature page
    signed_pdf_url = None
    signed_pdf_hash = None
    pdf_status = None

    try:
        pdf_html = wrap_signed_html_for_pdf(
            signed_html=signed_html,
            signature_data=signature_data,
            signer_name=signer_name,
            signer_email=signer_email,
            signed_at=now,
        )
        filename = f"proposal-{full_proposal_id[:8]}-signed.pdf"
        pdf_bytes = generate_pdf_docraptor(pdf_html, filename)
        signed_pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()
        signed_pdf_url = upload_proposal_pdf(
            org_id, f"{full_proposal_id}-signed", pdf_bytes
        )
        pdf_status = f"success: PDF generated ({len(pdf_bytes)} bytes)"
    except Exception as e:
        # PDF generation is non-blocking — signing still succeeds
        import logging
        logging.error(f"PDF generation failed for proposal {full_proposal_id}: {e}")
        pdf_status = f"error: {str(e)}"

    # =========================================================================
    # INSERT PROPOSAL SIGNATURE RECORD
    # =========================================================================
    signature_record = {
        "proposal_id": full_proposal_id,
        "org_id": org_id,
        "signer_name": signer_name,
        "signer_email": signer_email,
        "signature_data": signature_data,
        "signed_html": signed_html,
        "signer_ip": signer_ip,
        "signer_user_agent": signer_user_agent,
        "server_signed_at": now,
        "signed_pdf_url": signed_pdf_url,
        "signed_pdf_hash": signed_pdf_hash,
    }
    try:
        supabase.table("proposal_signatures").insert(signature_record).execute()
    except Exception as e:
        import logging
        logging.error(f"Failed to insert proposal_signature for {full_proposal_id}: {e}")

    # Populate client fields from signer data only if currently empty
    update_data = {
        "status": 2,
        "signed_at": now,
        "updated_at": now,
        "signed_pdf_url": signed_pdf_url,
        "converted_order_id": order["id"],
        "converted_engagement_id": engagement["id"],
        "account_id": account_id,
    }
    if signer_email and not proposal.get("client_email"):
        update_data["client_email"] = signer_email
    if signer_name and not proposal.get("client_name_f"):
        # Split "First Last" into first/last name
        parts = signer_name.strip().split(None, 1)
        update_data["client_name_f"] = parts[0]
        update_data["client_name_l"] = parts[1] if len(parts) > 1 else ""

    supabase.table("proposals").update(update_data).eq("id", full_proposal_id).execute()

    # =========================================================================
    # SEND EMAIL NOTIFICATIONS
    # =========================================================================
    # Get org notification config
    org_notify_result = supabase.table("organizations").select(
        "notification_email, domain"
    ).eq("id", org_id).execute()

    if org_notify_result.data:
        org_notify = org_notify_result.data[0]
        org_domain = org_notify.get("domain")
        notify_email = org_notify.get("notification_email")

        if org_domain and notify_email:
            from_email = f"billing@{org_domain}"
            to_emails = [notify_email]
            if signer_email:
                to_emails.append(signer_email)

            send_proposal_signed_email(
                to_emails=to_emails,
                from_email=from_email,
                signer_name=signer_name or client_name,
                company_name=proposal.get("client_company"),
                total=format_currency(proposal.get("total")),
                signed_pdf_url=signed_pdf_url,
                proposal_id=full_proposal_id,
            )

    return {
        "success": True,
        "signed_at": now,
        "proposal_id": full_proposal_id,
        "account_id": account_id,
        "contact_id": contact_id,
        "engagement_id": engagement["id"],
        "order_id": order["id"],
        "checkout_url": checkout_url,
        "signed_pdf_url": signed_pdf_url,
        "pdf_status": pdf_status,  # For debugging: shows if signed_html was received and PDF result
        "projects": [{"id": p["id"], "name": p["name"]} for p in projects_created],
    }


# =============================================================================
# WEBHOOK ENDPOINTS
# =============================================================================

webhook_router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])


@webhook_router.post("/stripe")
async def stripe_webhook(request: Request) -> dict[str, str]:
    """
    Handle Stripe webhook events.

    Processes checkout.session.completed events to:
    - Update order status to In Progress (paid)
    - Store payment_intent_id and paid_at timestamp
    """
    supabase = get_supabase()

    # Get raw body for signature verification
    try:
        payload = await request.body()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request body")

    signature = request.headers.get("stripe-signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")

    # Parse payload to get metadata
    try:
        event_data = json.loads(payload)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = event_data.get("type")

    # Route by event type
    if event_type == "checkout.session.completed":
        return await _handle_checkout_completed(supabase, event_data, payload, signature)
    elif event_type == "payment_intent.succeeded":
        return await _handle_payment_intent_succeeded(supabase, event_data, payload, signature)
    else:
        return {"status": "ignored", "event": event_type or "unknown"}


async def _handle_checkout_completed(
    supabase, event_data: dict, payload: bytes, signature: str
) -> dict[str, str]:
    """Handle checkout.session.completed — updates order status."""
    session = event_data.get("data", {}).get("object", {})
    metadata = session.get("metadata", {})

    org_id = metadata.get("org_id")
    order_id = metadata.get("order_id")

    if not org_id or not order_id:
        return {"status": "ignored", "reason": "missing_metadata"}

    # Verify webhook signature
    org_result = supabase.table("organizations").select(
        "stripe_webhook_secret"
    ).eq("id", org_id).execute()

    if org_result.data:
        webhook_secret = org_result.data[0].get("stripe_webhook_secret")
        if webhook_secret:
            verified_event = verify_webhook_signature(payload, signature, webhook_secret)
            if verified_event is None:
                raise HTTPException(status_code=400, detail="Invalid signature")

    payment_intent_id = session.get("payment_intent")
    now = datetime.now(timezone.utc).isoformat()

    update_result = supabase.table("orders").update({
        "status": 1,  # In Progress (paid)
        "paid_at": now,
        "stripe_payment_intent_id": payment_intent_id,
    }).eq("id", order_id).eq("org_id", org_id).execute()

    if not update_result.data:
        return {"status": "error", "reason": "order_not_found"}

    return {
        "status": "success",
        "order_id": order_id,
        "payment_intent_id": payment_intent_id or "",
    }


async def _handle_payment_intent_succeeded(
    supabase, event_data: dict, payload: bytes, signature: str
) -> dict[str, str]:
    """Handle payment_intent.succeeded — for Stripe Elements payments."""
    intent = event_data.get("data", {}).get("object", {})
    metadata = intent.get("metadata", {})

    org_id = metadata.get("org_id")
    proposal_id = metadata.get("proposal_id")

    if not org_id:
        return {"status": "ignored", "reason": "missing_org_id"}

    # Verify webhook signature
    org_result = supabase.table("organizations").select(
        "stripe_webhook_secret"
    ).eq("id", org_id).execute()

    if org_result.data:
        webhook_secret = org_result.data[0].get("stripe_webhook_secret")
        if webhook_secret:
            verified_event = verify_webhook_signature(payload, signature, webhook_secret)
            if verified_event is None:
                raise HTTPException(status_code=400, detail="Invalid signature")

    payment_intent_id = intent.get("id")
    amount = intent.get("amount_received", 0)
    now = datetime.now(timezone.utc).isoformat()

    # If there's an order linked via metadata, update it
    order_id = metadata.get("order_id")
    if order_id:
        supabase.table("orders").update({
            "status": 1,
            "paid_at": now,
            "stripe_payment_intent_id": payment_intent_id,
        }).eq("id", order_id).eq("org_id", org_id).execute()

    return {
        "status": "success",
        "event": "payment_intent.succeeded",
        "payment_intent_id": payment_intent_id or "",
        "proposal_id": proposal_id or "",
        "amount": amount,
    }
