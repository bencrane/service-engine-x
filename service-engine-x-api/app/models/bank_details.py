"""Organization bank details models for request/response schemas."""

from pydantic import BaseModel, Field


class BankDetailsCreate(BaseModel):
    """Request body for creating/replacing org bank details."""

    account_name: str = Field(..., min_length=1, max_length=255)
    account_number: str | None = Field(None, max_length=34)
    routing_number: str | None = Field(None, max_length=9)
    bank_name: str | None = Field(None, max_length=255)
    bank_address_line1: str | None = Field(None, max_length=255)
    bank_address_line2: str | None = Field(None, max_length=255)
    bank_city: str | None = Field(None, max_length=100)
    bank_state: str | None = Field(None, max_length=100)
    bank_postal_code: str | None = Field(None, max_length=20)
    bank_country: str | None = Field(None, max_length=2, description="ISO 3166-1 alpha-2")
    swift_code: str | None = Field(None, max_length=11)
    iban: str | None = Field(None, max_length=34)


class BankDetailsUpdate(BaseModel):
    """Request body for partially updating org bank details."""

    account_name: str | None = Field(None, min_length=1, max_length=255)
    account_number: str | None = Field(None, max_length=34)
    routing_number: str | None = Field(None, max_length=9)
    bank_name: str | None = Field(None, max_length=255)
    bank_address_line1: str | None = Field(None, max_length=255)
    bank_address_line2: str | None = Field(None, max_length=255)
    bank_city: str | None = Field(None, max_length=100)
    bank_state: str | None = Field(None, max_length=100)
    bank_postal_code: str | None = Field(None, max_length=20)
    bank_country: str | None = Field(None, max_length=2, description="ISO 3166-1 alpha-2")
    swift_code: str | None = Field(None, max_length=11)
    iban: str | None = Field(None, max_length=34)


class BankDetailsResponse(BaseModel):
    """Organization bank details response schema."""

    id: str
    org_id: str
    account_name: str
    account_number: str | None = None
    routing_number: str | None = None
    bank_name: str | None = None
    bank_address_line1: str | None = None
    bank_address_line2: str | None = None
    bank_city: str | None = None
    bank_state: str | None = None
    bank_postal_code: str | None = None
    bank_country: str | None = None
    swift_code: str | None = None
    iban: str | None = None
    created_at: str
    updated_at: str
