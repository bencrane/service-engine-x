"""Proposal models for request/response schemas."""

from pydantic import BaseModel, EmailStr, Field


# Status mapping: 0=Draft, 1=Sent, 2=Signed, 3=Rejected
PROPOSAL_STATUS_MAP: dict[int, str] = {
    0: "Draft",
    1: "Sent",
    2: "Signed",
    3: "Rejected",
}


class ProposalItemInput(BaseModel):
    """Input schema for proposal item (defines a project to be created)."""

    name: str = Field(min_length=1, description="Project name")
    description: str = Field(min_length=1, description="Project scope/description")
    price: float = Field(ge=0, description="Project price")
    service_id: str | None = Field(default=None, description="Optional service template reference")


class CreateProposalRequest(BaseModel):
    """Request body for creating a proposal."""

    client_email: EmailStr
    client_name_f: str = Field(min_length=1)
    client_name_l: str = Field(min_length=1)
    client_company: str | None = None
    items: list[ProposalItemInput] = Field(min_length=1)
    notes: str | None = None


class ProposalItemResponse(BaseModel):
    """Response schema for proposal item (represents a project to be created)."""

    id: str
    name: str
    description: str | None
    price: str
    service_id: str | None = None
    created_at: str


class ProposalResponse(BaseModel):
    """Response schema for a single proposal."""

    id: str
    client_email: str
    client_name: str
    client_name_f: str
    client_name_l: str
    client_company: str | None
    status: str
    status_id: int
    total: str
    notes: str | None
    created_at: str
    updated_at: str
    sent_at: str | None
    signed_at: str | None
    pdf_url: str | None = None
    converted_order_id: str | None
    converted_engagement_id: str | None = None
    items: list[ProposalItemResponse] = []


class ProposalListItem(BaseModel):
    """Response schema for proposal in list (without items)."""

    id: str
    client_email: str
    client_name: str
    client_name_f: str
    client_name_l: str
    client_company: str | None
    status: str
    status_id: int
    total: str
    notes: str | None
    created_at: str
    updated_at: str
    sent_at: str | None
    signed_at: str | None
    pdf_url: str | None = None
    converted_order_id: str | None
    converted_engagement_id: str | None = None


class ProposalListLinks(BaseModel):
    """Pagination links for proposal list."""

    first: str
    last: str
    prev: str | None
    next: str | None


class ProposalListMetaLink(BaseModel):
    """Individual pagination link in meta."""

    url: str | None
    label: str
    active: bool


class ProposalListMeta(BaseModel):
    """Pagination metadata for proposal list."""

    current_page: int
    from_: int = Field(alias="from")
    to: int
    last_page: int
    per_page: int
    total: int
    path: str
    links: list[ProposalListMetaLink]

    model_config = {"populate_by_name": True}


class ProposalListResponse(BaseModel):
    """Response schema for paginated proposal list."""

    data: list[ProposalListItem]
    links: ProposalListLinks
    meta: ProposalListMeta
