"""Proposals API router."""

import io
import json
import os
import secrets
import string
from datetime import datetime, timezone
from typing import Any

import requests
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.auth.dependencies import AuthContext, get_current_org
from app.database import get_supabase
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

# DocRaptor / Documenso configuration
DOCRAPTOR_API_KEY = os.environ.get("DOCRAPTOR_API_KEY", "oUcqyfynOYOBkEIV8_IU")
DOCUMENSO_API_KEY = os.environ.get("DOCUMENSO_API_KEY", "api_r4fv8167lra8c3dh")
DOCUMENSO_URL = os.environ.get("DOCUMENSO_URL", "https://app.documenso.com")


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
            <div class="item-header">
                <span class="item-name">{item_name}</span>
                <span class="item-price">${item_price:,.2f}</span>
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
            margin: 1in;
        }}

        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #1a1a1a;
        }}

        .header {{
            border-bottom: 3px solid #2563eb;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}

        .logo {{
            font-size: 24pt;
            font-weight: bold;
            color: #2563eb;
            margin-bottom: 5px;
        }}

        .title {{
            font-size: 28pt;
            font-weight: bold;
            color: #1a1a1a;
            margin: 40px 0 10px 0;
        }}

        .subtitle {{
            font-size: 14pt;
            color: #666;
            margin-bottom: 30px;
        }}

        .meta {{
            background: #f8fafc;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}

        .meta-row {{
            margin-bottom: 8px;
        }}

        .meta-label {{
            font-weight: bold;
            color: #666;
            display: inline-block;
            width: 120px;
        }}

        .meta-value {{
            color: #1a1a1a;
        }}

        .section {{
            margin-bottom: 30px;
        }}

        .section h2 {{
            font-size: 16pt;
            color: #2563eb;
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 8px;
            margin-bottom: 15px;
        }}

        .item {{
            background: #f8fafc;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #2563eb;
        }}

        .item-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}

        .item-name {{
            font-weight: bold;
            font-size: 12pt;
            color: #1a1a1a;
        }}

        .item-price {{
            font-weight: bold;
            font-size: 12pt;
            color: #2563eb;
        }}

        .item-description {{
            color: #666;
            font-size: 10pt;
            margin: 0;
        }}

        .total-box {{
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            text-align: right;
            margin: 30px 0;
        }}

        .total-label {{
            font-size: 11pt;
            text-transform: uppercase;
            letter-spacing: 2px;
            opacity: 0.9;
        }}

        .total-value {{
            font-size: 32pt;
            font-weight: bold;
            margin-top: 5px;
        }}

        .notes {{
            background: #fffbeb;
            border-left: 4px solid #f59e0b;
            padding: 15px 20px;
            margin: 20px 0;
        }}

        .notes h3 {{
            color: #b45309;
            margin: 0 0 8px 0;
            font-size: 11pt;
        }}

        .notes p {{
            margin: 0;
            color: #92400e;
        }}

        .signature-area {{
            margin-top: 60px;
            padding-top: 30px;
            border-top: 1px solid #e5e7eb;
        }}

        .signature-line {{
            border-bottom: 1px solid #1a1a1a;
            width: 250px;
            margin-top: 40px;
        }}

        .signature-label {{
            font-size: 10pt;
            color: #666;
            margin-top: 5px;
        }}

        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            font-size: 10pt;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">{org_name}</div>
    </div>

    <div class="title">Proposal</div>
    <div class="subtitle">Prepared for {client_company or client_name}</div>

    <div class="meta">
        <div class="meta-row">
            <span class="meta-label">Prepared For:</span>
            <span class="meta-value">{client_name}</span>
        </div>
        {"<div class='meta-row'><span class='meta-label'>Company:</span><span class='meta-value'>" + client_company + "</span></div>" if client_company else ""}
        <div class="meta-row">
            <span class="meta-label">Email:</span>
            <span class="meta-value">{client_email}</span>
        </div>
        <div class="meta-row">
            <span class="meta-label">Date:</span>
            <span class="meta-value">{proposal_date}</span>
        </div>
    </div>

    <div class="section">
        <h2>Scope of Work</h2>
        {items_html}
    </div>

    <div class="total-box">
        <div class="total-label">Total Investment</div>
        <div class="total-value">{formatted_total}</div>
    </div>

    {"<div class='notes'><h3>Notes</h3><p>" + notes + "</p></div>" if notes else ""}

    <div class="signature-area">
        <p>By signing below, you agree to the scope of work and investment outlined in this proposal.</p>
        <div class="signature-line"></div>
        <div class="signature-label">Signature &amp; Date</div>
    </div>

    <div class="footer">
        <p>Thank you for your business.</p>
    </div>
</body>
</html>
"""


def generate_pdf_docraptor(html_content: str, filename: str) -> bytes:
    """Convert HTML to PDF using DocRaptor API."""
    import docraptor

    doc_api = docraptor.DocApi()
    doc_api.api_client.configuration.username = DOCRAPTOR_API_KEY

    pdf_bytes = doc_api.create_doc({
        "test": False,  # Production mode - no watermark
        "document_type": "pdf",
        "document_content": html_content,
        "name": filename,
    })
    return pdf_bytes


def upload_to_documenso(
    pdf_bytes: bytes,
    filename: str,
    recipient_name: str,
    recipient_email: str,
    title: str,
) -> dict[str, Any]:
    """
    Upload PDF to Documenso and create signing document.
    Returns dict with document_id and signing_token.
    """
    # Strip /api/v1 or /api/v2 if present to get base URL
    documenso_base = DOCUMENSO_URL.replace("/api/v1", "").replace("/api/v2", "")

    # Create document with recipient
    payload = {
        "title": title,
        "recipients": [
            {
                "email": recipient_email,
                "name": recipient_name,
                "role": "SIGNER",
                "signingOrder": 1,
            }
        ]
    }

    files = {
        "file": (filename, io.BytesIO(pdf_bytes), "application/pdf"),
    }

    create_resp = requests.post(
        f"{documenso_base}/api/v2/document/create",
        headers={"Authorization": DOCUMENSO_API_KEY},
        files=files,
        data={"payload": json.dumps(payload)},
        timeout=30,
    )

    if not create_resp.ok:
        raise HTTPException(
            status_code=500,
            detail=f"Documenso upload failed: {create_resp.status_code} - {create_resp.text[:200]}",
        )

    doc_data = create_resp.json()
    document_id = doc_data.get("documentId") or doc_data.get("id")

    # Get signing token from recipients
    recipients = doc_data.get("recipients", [])
    signing_token = None
    recipient_id = None

    if recipients:
        signing_token = recipients[0].get("token") or recipients[0].get("signingToken")
        recipient_id = recipients[0].get("id")

    # If no token in response, fetch it
    if not signing_token:
        get_resp = requests.get(
            f"{documenso_base}/api/v1/documents/{document_id}",
            headers={"Authorization": f"Bearer {DOCUMENSO_API_KEY}"},
            timeout=30,
        )
        if get_resp.ok:
            doc_detail = get_resp.json()
            recipients = doc_detail.get("recipients", [])
            if recipients:
                signing_token = recipients[0].get("token") or recipients[0].get("signingToken")
                recipient_id = recipients[0].get("id")

    # Add signature field
    if recipient_id:
        requests.post(
            f"{documenso_base}/api/v1/documents/{document_id}/fields",
            headers={
                "Authorization": f"Bearer {DOCUMENSO_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "type": "SIGNATURE",
                "recipientId": recipient_id,
                "pageNumber": 1,
                "pageX": 100,
                "pageY": 650,
                "pageWidth": 200,
                "pageHeight": 60,
            },
            timeout=30,
        )

    # Activate document (no email - we embed instead)
    requests.post(
        f"{documenso_base}/api/v1/documents/{document_id}/send",
        headers={
            "Authorization": f"Bearer {DOCUMENSO_API_KEY}",
            "Content-Type": "application/json",
        },
        json={"sendEmail": False},
        timeout=30,
    )

    return {
        "document_id": str(document_id),
        "signing_token": signing_token or "",
    }


def serialize_proposal_list_item(proposal: dict[str, Any]) -> ProposalListItem:
    """Serialize a proposal for list response (without items)."""
    status_id = proposal.get("status", 0)
    return ProposalListItem(
        id=proposal["id"],
        client_email=proposal["client_email"],
        client_name=f"{proposal.get('client_name_f', '')} {proposal.get('client_name_l', '')}".strip(),
        client_name_f=proposal.get("client_name_f", ""),
        client_name_l=proposal.get("client_name_l", ""),
        client_company=proposal.get("client_company"),
        status=PROPOSAL_STATUS_MAP.get(status_id, "Unknown"),
        status_id=status_id,
        total=str(proposal.get("total", "0.00")),
        notes=proposal.get("notes"),
        created_at=proposal["created_at"],
        updated_at=proposal["updated_at"],
        sent_at=proposal.get("sent_at"),
        signed_at=proposal.get("signed_at"),
        converted_order_id=proposal.get("converted_order_id"),
        converted_engagement_id=proposal.get("converted_engagement_id"),
    )


def serialize_proposal_item(item: dict[str, Any]) -> ProposalItemResponse:
    """Serialize a proposal item."""
    return ProposalItemResponse(
        id=item["id"],
        name=item["name"],
        description=item.get("description"),
        price=str(item.get("price", "0.00")),
        service_id=item.get("service_id"),
        created_at=item["created_at"],
    )


def serialize_proposal(proposal: dict[str, Any], items: list[dict[str, Any]]) -> ProposalResponse:
    """Serialize a proposal with items."""
    status_id = proposal.get("status", 0)
    return ProposalResponse(
        id=proposal["id"],
        client_email=proposal["client_email"],
        client_name=f"{proposal.get('client_name_f', '')} {proposal.get('client_name_l', '')}".strip(),
        client_name_f=proposal.get("client_name_f", ""),
        client_name_l=proposal.get("client_name_l", ""),
        client_company=proposal.get("client_company"),
        status=PROPOSAL_STATUS_MAP.get(status_id, "Unknown"),
        status_id=status_id,
        total=str(proposal.get("total", "0.00")),
        notes=proposal.get("notes"),
        created_at=proposal["created_at"],
        updated_at=proposal["updated_at"],
        sent_at=proposal.get("sent_at"),
        signed_at=proposal.get("signed_at"),
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
    count_result = await supabase.table("proposals").select(
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
        services_result = await supabase.table("services").select("id").eq(
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

    # Create proposal
    proposal_data = {
        "org_id": auth.org_id,
        "client_email": body.client_email.lower().strip(),
        "client_name_f": body.client_name_f.strip(),
        "client_name_l": body.client_name_l.strip(),
        "client_company": body.client_company,
        "status": 0,  # Draft
        "total": total,
        "notes": body.notes,
    }

    proposal_result = await supabase.table("proposals").insert(proposal_data).select().execute()

    if not proposal_result.data:
        raise HTTPException(status_code=500, detail="Failed to create proposal")

    proposal = proposal_result.data[0]

    # Create proposal items (each defines a project)
    item_rows = [
        {
            "proposal_id": proposal["id"],
            "name": item.name,
            "description": item.description,
            "price": item.price,
            "service_id": item.service_id,
        }
        for item in body.items
    ]

    items_result = await supabase.table("proposal_items").insert(item_rows).select("*").execute()

    if not items_result.data:
        # Clean up proposal if items failed
        await supabase.table("proposals").delete().eq("id", proposal["id"]).execute()
        raise HTTPException(status_code=500, detail="Failed to create proposal items")

    return serialize_proposal(proposal, items_result.data)


@router.get("/{proposal_id}", response_model=ProposalResponse)
async def retrieve_proposal(
    proposal_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> ProposalResponse:
    """Retrieve a proposal by ID."""
    supabase = get_supabase()

    # Fetch proposal with items
    result = await supabase.table("proposals").select(
        "*, proposal_items (*)"
    ).eq("id", proposal_id).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Not Found")

    proposal = result.data[0]
    items = proposal.get("proposal_items") or []

    return serialize_proposal(proposal, items)


@router.post("/{proposal_id}/send", response_model=ProposalResponse)
async def send_proposal(
    proposal_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> ProposalResponse:
    """
    Send a proposal (Draft -> Sent).

    This endpoint:
    1. Generates a PDF of the proposal using DocRaptor
    2. Uploads the PDF to Documenso for e-signature
    3. Stores the signing token on the proposal
    4. Updates status to Sent
    """
    supabase = get_supabase()

    # Fetch proposal with items
    result = await supabase.table("proposals").select(
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
    org_result = await supabase.table("organizations").select("name").eq("id", auth.org_id).execute()
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

    # Upload to Documenso
    client_email = proposal.get("client_email", "")
    title = f"Proposal - {proposal.get('client_company') or client_name}"

    try:
        documenso_result = upload_to_documenso(
            pdf_bytes=pdf_bytes,
            filename=filename,
            recipient_name=client_name,
            recipient_email=client_email,
            title=title,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload to Documenso: {str(e)}",
        )

    # Update proposal with Documenso info and status
    now = datetime.now(timezone.utc).isoformat()

    await supabase.table("proposals").update({
        "status": 1,
        "sent_at": now,
        "updated_at": now,
        "documenso_document_id": documenso_result["document_id"],
        "documenso_signing_token": documenso_result["signing_token"],
    }).eq("id", proposal_id).execute()

    # Update local proposal dict for response
    proposal["status"] = 1
    proposal["sent_at"] = now
    proposal["updated_at"] = now
    proposal["documenso_document_id"] = documenso_result["document_id"]
    proposal["documenso_signing_token"] = documenso_result["signing_token"]

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
    result = await supabase.table("proposals").select(
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

    existing_user_result = await supabase.table("users").select("id").eq(
        "email", proposal["client_email"]
    ).eq("org_id", auth.org_id).execute()

    if existing_user_result.data:
        client_id = existing_user_result.data[0]["id"]
    else:
        # Get client role (dashboard_access = 0)
        role_result = await supabase.table("roles").select("id").eq(
            "dashboard_access", 0
        ).execute()

        if role_result.data:
            # Create new user
            new_user_result = await supabase.table("users").insert({
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
            }).select("id").execute()

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

    engagement_result = await supabase.table("engagements").insert(engagement_data).select().execute()

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

        project_result = await supabase.table("projects").insert(project_data).select().execute()

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

    order_result = await supabase.table("orders").insert(order_data).select().execute()

    if not order_result.data:
        raise HTTPException(status_code=500, detail="Failed to create order")

    order = order_result.data[0]

    # =========================================================================
    # UPDATE PROPOSAL
    # =========================================================================
    await supabase.table("proposals").update({
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


@public_router.get("/{proposal_id}")
async def get_public_proposal(proposal_id: str) -> dict[str, Any]:
    """
    Get proposal data for public viewing/signing.
    No authentication required - used by client-facing proposal pages.

    Returns proposal details and Documenso signing token for embedding.
    """
    supabase = get_supabase()

    # Fetch proposal with items and org info
    result = await supabase.table("proposals").select(
        "*, proposal_items (*), organizations:org_id (name)"
    ).eq("id", proposal_id).is_("deleted_at", "null").execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Proposal not found")

    proposal = result.data[0]

    # Only allow viewing if proposal has been sent
    if proposal["status"] < 1:
        raise HTTPException(status_code=404, detail="Proposal not found")

    items = proposal.get("proposal_items") or []
    org = proposal.get("organizations") or {}

    # Check if already signed
    is_signed = proposal["status"] == 2

    return {
        "id": proposal["id"],
        "org_name": org.get("name", ""),
        "client_name": f"{proposal.get('client_name_f', '')} {proposal.get('client_name_l', '')}".strip(),
        "client_company": proposal.get("client_company"),
        "client_email": proposal.get("client_email"),
        "status": PROPOSAL_STATUS_MAP.get(proposal["status"], "Unknown"),
        "status_id": proposal["status"],
        "total": str(proposal.get("total", "0.00")),
        "notes": proposal.get("notes"),
        "sent_at": proposal.get("sent_at"),
        "signed_at": proposal.get("signed_at"),
        "is_signed": is_signed,
        "signing_token": proposal.get("documenso_signing_token") if not is_signed else None,
        "documenso_document_id": proposal.get("documenso_document_id"),
        "items": [
            {
                "id": item["id"],
                "name": item["name"],
                "description": item.get("description"),
                "price": str(item.get("price", "0.00")),
            }
            for item in items
        ],
    }


# =============================================================================
# WEBHOOK ENDPOINTS (For Documenso callbacks)
# =============================================================================

webhook_router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])


@webhook_router.post("/documenso")
async def documenso_webhook(request: Request) -> dict[str, str]:
    """
    Handle Documenso webhook events.

    When a document is signed, this triggers the proposal signing flow:
    - Creates engagement, projects, and order
    - Updates proposal status to Signed
    """
    supabase = get_supabase()

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = payload.get("event") or payload.get("type")
    document_id = payload.get("documentId") or payload.get("document_id")

    # We only care about completed/signed events
    if event_type not in ["DOCUMENT_COMPLETED", "document.completed", "DOCUMENT_SIGNED", "document.signed"]:
        return {"status": "ignored", "event": event_type or "unknown"}

    if not document_id:
        raise HTTPException(status_code=400, detail="Missing document_id")

    # Find proposal by Documenso document ID
    result = await supabase.table("proposals").select(
        "*, proposal_items (*)"
    ).eq("documenso_document_id", str(document_id)).is_("deleted_at", "null").execute()

    if not result.data:
        # Document not found - might be from a different system
        return {"status": "ignored", "reason": "document_not_found"}

    proposal = result.data[0]

    # Skip if already signed
    if proposal["status"] == 2:
        return {"status": "already_signed", "proposal_id": proposal["id"]}

    # Skip if not in Sent status
    if proposal["status"] != 1:
        return {"status": "ignored", "reason": f"proposal_status_{proposal['status']}"}

    # Trigger the signing flow
    now = datetime.now(timezone.utc).isoformat()
    items = proposal.get("proposal_items") or []
    org_id = proposal["org_id"]

    # Find or create client user
    client_id: str | None = None

    existing_user_result = await supabase.table("users").select("id").eq(
        "email", proposal["client_email"]
    ).eq("org_id", org_id).execute()

    if existing_user_result.data:
        client_id = existing_user_result.data[0]["id"]
    else:
        role_result = await supabase.table("roles").select("id").eq(
            "dashboard_access", 0
        ).execute()

        if role_result.data:
            new_user_result = await supabase.table("users").insert({
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
            }).select("id").execute()

            if new_user_result.data:
                client_id = new_user_result.data[0]["id"]

    # Create engagement
    client_name = f"{proposal['client_name_f']} {proposal['client_name_l']}".strip()
    engagement_name = f"{client_name} - {proposal.get('notes', 'Engagement')[:50] if proposal.get('notes') else 'New Engagement'}"

    engagement_result = await supabase.table("engagements").insert({
        "org_id": org_id,
        "client_id": client_id,
        "name": engagement_name,
        "status": 1,
        "proposal_id": proposal["id"],
        "created_at": now,
        "updated_at": now,
    }).select().execute()

    if not engagement_result.data:
        raise HTTPException(status_code=500, detail="Failed to create engagement")

    engagement = engagement_result.data[0]

    # Create projects
    for item in items:
        await supabase.table("projects").insert({
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

    # Create order
    primary_item = items[0] if items else None
    order_name = primary_item["name"] if primary_item else "Proposal Order"

    order_result = await supabase.table("orders").insert({
        "org_id": org_id,
        "number": generate_order_number(),
        "user_id": client_id,
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
            "proposal_id": proposal["id"],
            "engagement_id": engagement["id"],
            "signed_via": "documenso_webhook",
        },
    }).select().execute()

    order = order_result.data[0] if order_result.data else None

    # Update proposal
    await supabase.table("proposals").update({
        "status": 2,
        "signed_at": now,
        "updated_at": now,
        "converted_order_id": order["id"] if order else None,
        "converted_engagement_id": engagement["id"],
    }).eq("id", proposal["id"]).execute()

    return {
        "status": "signed",
        "proposal_id": proposal["id"],
        "engagement_id": engagement["id"],
        "order_id": order["id"] if order else None,
    }
