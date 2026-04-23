"""Meeting model schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


VALID_MEETING_STATUSES = {
    "pending",
    "scheduled",
    "in_progress",
    "completed",
    "cancelled",
    "rejected",
    "no_show",
    "rescheduled",
}

UPCOMING_MEETING_STATUSES = ("pending", "scheduled")


class AccountSummary(BaseModel):
    id: str
    name: str
    lifecycle: str | None = None


class ContactSummary(BaseModel):
    id: str
    name: str
    email: str | None = None


class DealSummary(BaseModel):
    id: str
    name: str | None = None
    stage: str | None = None
    amount: str | None = None


class MeetingListResponse(BaseModel):
    id: str
    org_id: str
    account_id: str | None = None
    contact_id: str | None = None
    deal_id: str | None = None
    cal_event_uid: str | None = None
    cal_booking_id: int | None = None
    title: str
    start_time: datetime
    end_time: datetime
    status: str
    organizer_email: str | None = None
    attendee_emails: list[str] = Field(default_factory=list)
    host_no_show: bool = False
    guest_no_show: bool = False
    account: AccountSummary | None = None
    contact: ContactSummary | None = None
    deal: DealSummary | None = None
    created_at: datetime
    updated_at: datetime


class MeetingResponse(MeetingListResponse):
    cancellation_reason: str | None = None
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None
    recording_url: str | None = None
    transcript_url: str | None = None
