#!/usr/bin/env python3
"""Create a test proposal for Revenue Activation."""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("../.env.local")


def main():
    # Revenue Activation org ID
    ORG_ID = "11111111-1111-1111-1111-111111111111"

    # Client details
    CLIENT_NAME_F = "Sarah"
    CLIENT_NAME_L = "Chen"
    CLIENT_COMPANY = "Greenfield Partners"
    CLIENT_EMAIL = "benjaminjcrane+sarah@gmail.com"

    # Proposal items (projects)
    ITEMS = [
        {
            "name": "CRM Data Cleaning",
            "description": "Full audit and cleanup of your CRM data. Includes deduplication, field standardization, enrichment of missing contact info, and validation of email addresses. Deliverable: Clean, normalized CRM export with detailed change log.",
            "price": 3500.00,
        },
        {
            "name": "TAM Build Out",
            "description": "Total Addressable Market analysis and prospect list creation. Includes ICP definition, firmographic filtering, contact sourcing, and CRM-ready import file. Deliverable: 500+ qualified accounts with key decision-maker contacts.",
            "price": 4500.00,
        },
    ]

    TOTAL = sum(item["price"] for item in ITEMS)
    NOTES = "Payment due upon signing. Work begins within 5 business days of signed agreement."

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

    # Create proposal items
    for item in ITEMS:
        item_data = {
            "proposal_id": proposal_id,
            "name": item["name"],
            "description": item["description"],
            "price": item["price"],
        }
        supabase.table("proposal_items").insert(item_data).execute()

    print("\n" + "=" * 60)
    print("PROPOSAL CREATED")
    print("=" * 60)
    print(f"\nProposal ID: {proposal_id}")
    print(f"Short ID:    {short_id}")
    print(f"\nClient: {CLIENT_NAME_F} {CLIENT_NAME_L}")
    print(f"Company: {CLIENT_COMPANY}")
    print(f"Email: {CLIENT_EMAIL}")
    print(f"\nProjects:")
    for item in ITEMS:
        print(f"  - {item['name']}: ${item['price']:,.2f}")
    print(f"\nTotal: ${TOTAL:,.2f}")
    print(f"\nPublic URL: https://revenueactivation.com/proposal/{short_id}")
    print("=" * 60)


if __name__ == "__main__":
    main()
