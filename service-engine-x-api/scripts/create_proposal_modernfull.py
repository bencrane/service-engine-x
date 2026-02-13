#!/usr/bin/env python3
"""Create a one-off proposal for Modern Full / Uraiv."""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("../.env.local")


def main():
    # Modern Full org ID
    ORG_ID = "9c187159-adc1-4cdd-af84-5c309d1ccdd8"

    # Client details
    CLIENT_NAME_F = "Max"
    CLIENT_NAME_L = "Hirsch"
    CLIENT_COMPANY = "Uraiv, LLC"
    CLIENT_EMAIL = "benjaminjcrane+max@gmail.com"

    # Proposal details
    TOTAL = 4000.00
    NOTES = "Custom project"

    supabase = create_client(
        os.environ.get("SUPABASE_URL") or os.environ["SERVICE_ENGINE_X_SUPABASE_URL"],
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ["SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY"],
    )

    # Create proposal with status=1 (Sent) so it's viewable
    proposal_data = {
        "org_id": ORG_ID,
        "client_email": CLIENT_EMAIL,
        "client_name_f": CLIENT_NAME_F,
        "client_name_l": CLIENT_NAME_L,
        "client_company": CLIENT_COMPANY,
        "status": 1,  # Sent - viewable on frontend
        "total": TOTAL,
        "notes": NOTES,
    }

    result = supabase.table("proposals").insert(proposal_data).execute()

    if not result.data:
        print("ERROR: Failed to create proposal")
        return

    proposal = result.data[0]
    proposal_id = proposal["id"]
    short_id = proposal_id[:8]

    print("\n" + "=" * 60)
    print("PROPOSAL CREATED")
    print("=" * 60)
    print(f"\nProposal ID: {proposal_id}")
    print(f"Short ID:    {short_id}")
    print(f"\nClient: {CLIENT_NAME_F} {CLIENT_NAME_L}")
    print(f"Company: {CLIENT_COMPANY}")
    print(f"Total: ${TOTAL:,.2f}")
    print(f"\nPublic URL: https://modernfull.com/proposal/{short_id}")
    print("=" * 60)


if __name__ == "__main__":
    main()
