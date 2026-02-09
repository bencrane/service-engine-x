"""Supabase Storage utilities for file uploads."""

from app.config import get_settings
from app.database import get_supabase

PROPOSALS_BUCKET = "proposals"


def upload_proposal_pdf(org_id: str, proposal_id: str, pdf_bytes: bytes) -> str:
    """
    Upload a proposal PDF to Supabase Storage.

    Stores at: proposals/{org_id}/{proposal_id}.pdf
    Returns the public URL for the uploaded file.
    """
    supabase = get_supabase()
    settings = get_settings()

    file_path = f"{org_id}/{proposal_id}.pdf"

    # Remove existing file if re-sending a proposal
    try:
        supabase.storage.from_(PROPOSALS_BUCKET).remove([file_path])
    except Exception:
        pass  # File may not exist yet

    # Upload the PDF
    supabase.storage.from_(PROPOSALS_BUCKET).upload(
        path=file_path,
        file=pdf_bytes,
        file_options={"content-type": "application/pdf"},
    )

    # Build the public URL
    supabase_url = settings.service_engine_x_supabase_url.rstrip("/")
    public_url = f"{supabase_url}/storage/v1/object/public/{PROPOSALS_BUCKET}/{file_path}"

    return public_url
