#!/usr/bin/env python3
"""Populate test data for Revenue Activation - Accounts, Contacts, and Proposals."""

import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("../.env.local")


def main():
    # Revenue Activation org ID
    ORG_ID = "11111111-1111-1111-1111-111111111111"

    supabase = create_client(
        os.environ.get("SUPABASE_URL") or os.environ["SERVICE_ENGINE_X_SUPABASE_URL"],
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ["SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY"],
    )

    now = datetime.now(timezone.utc).isoformat()

    # =========================================================================
    # CREATE TEST ACCOUNTS
    # =========================================================================
    accounts_data = [
        {
            "org_id": ORG_ID,
            "name": "Greenfield Partners",
            "domain": "greenfieldpartners.io",
            "lifecycle": "active",
            "source": "referral",
            "balance": 0.00,
            "total_spent": 8000.00,
            "note": "Long-term client, started with CRM cleanup",
            "created_at": now,
            "updated_at": now,
        },
        {
            "org_id": ORG_ID,
            "name": "TechStart Ventures",
            "domain": "techstartvc.com",
            "lifecycle": "lead",
            "source": "linkedin",
            "balance": 0.00,
            "total_spent": 0.00,
            "note": "Interested in TAM analysis",
            "created_at": now,
            "updated_at": now,
        },
        {
            "org_id": ORG_ID,
            "name": "Meridian Consulting",
            "domain": "meridianconsulting.co",
            "lifecycle": "active",
            "source": "website",
            "balance": 500.00,
            "total_spent": 12500.00,
            "note": "Monthly retainer client",
            "created_at": now,
            "updated_at": now,
        },
        {
            "org_id": ORG_ID,
            "name": "Apex Growth",
            "domain": "apexgrowth.io",
            "lifecycle": "inactive",
            "source": "cold_outreach",
            "balance": 0.00,
            "total_spent": 3500.00,
            "note": "Completed one project, no follow-up",
            "created_at": now,
            "updated_at": now,
        },
    ]

    print("\n" + "=" * 60)
    print("CREATING ACCOUNTS")
    print("=" * 60)

    account_ids = {}
    for acc in accounts_data:
        # Check if account already exists
        existing = supabase.table("accounts").select("id").eq(
            "org_id", ORG_ID
        ).eq("name", acc["name"]).execute()

        if existing.data:
            account_ids[acc["name"]] = existing.data[0]["id"]
            print(f"  [EXISTS] {acc['name']}")
        else:
            result = supabase.table("accounts").insert(acc).execute()
            if result.data:
                account_ids[acc["name"]] = result.data[0]["id"]
                print(f"  [CREATED] {acc['name']} ({acc['lifecycle']})")
            else:
                print(f"  [ERROR] Failed to create {acc['name']}")

    # =========================================================================
    # CREATE TEST CONTACTS
    # =========================================================================
    contacts_data = [
        # Greenfield Partners contacts
        {
            "org_id": ORG_ID,
            "account_id": account_ids.get("Greenfield Partners"),
            "name_f": "Sarah",
            "name_l": "Chen",
            "email": "benjaminjcrane+sarah@gmail.com",
            "phone": "+1 (555) 123-4567",
            "title": "VP of Operations",
            "is_primary": True,
            "is_billing": True,
            "created_at": now,
            "updated_at": now,
        },
        {
            "org_id": ORG_ID,
            "account_id": account_ids.get("Greenfield Partners"),
            "name_f": "Michael",
            "name_l": "Torres",
            "email": "benjaminjcrane+michael@gmail.com",
            "phone": "+1 (555) 123-4568",
            "title": "Sales Director",
            "is_primary": False,
            "is_billing": False,
            "created_at": now,
            "updated_at": now,
        },
        # TechStart Ventures contacts
        {
            "org_id": ORG_ID,
            "account_id": account_ids.get("TechStart Ventures"),
            "name_f": "Jennifer",
            "name_l": "Park",
            "email": "benjaminjcrane+jennifer@gmail.com",
            "phone": "+1 (555) 234-5678",
            "title": "Managing Partner",
            "is_primary": True,
            "is_billing": True,
            "created_at": now,
            "updated_at": now,
        },
        # Meridian Consulting contacts
        {
            "org_id": ORG_ID,
            "account_id": account_ids.get("Meridian Consulting"),
            "name_f": "David",
            "name_l": "Williams",
            "email": "benjaminjcrane+david@gmail.com",
            "phone": "+1 (555) 345-6789",
            "title": "CEO",
            "is_primary": True,
            "is_billing": False,
            "created_at": now,
            "updated_at": now,
        },
        {
            "org_id": ORG_ID,
            "account_id": account_ids.get("Meridian Consulting"),
            "name_f": "Lisa",
            "name_l": "Thompson",
            "email": "benjaminjcrane+lisa@gmail.com",
            "phone": "+1 (555) 345-6790",
            "title": "Finance Director",
            "is_primary": False,
            "is_billing": True,
            "created_at": now,
            "updated_at": now,
        },
        # Apex Growth contacts
        {
            "org_id": ORG_ID,
            "account_id": account_ids.get("Apex Growth"),
            "name_f": "Robert",
            "name_l": "Kim",
            "email": "benjaminjcrane+robert@gmail.com",
            "phone": "+1 (555) 456-7890",
            "title": "Growth Lead",
            "is_primary": True,
            "is_billing": True,
            "created_at": now,
            "updated_at": now,
        },
    ]

    print("\n" + "=" * 60)
    print("CREATING CONTACTS")
    print("=" * 60)

    for contact in contacts_data:
        if not contact.get("account_id"):
            print(f"  [SKIP] {contact['name_f']} {contact['name_l']} - no account")
            continue

        # Check if contact already exists
        existing = supabase.table("contacts").select("id").eq(
            "org_id", ORG_ID
        ).eq("email", contact["email"]).execute()

        if existing.data:
            print(f"  [EXISTS] {contact['name_f']} {contact['name_l']} <{contact['email']}>")
        else:
            result = supabase.table("contacts").insert(contact).execute()
            if result.data:
                role = []
                if contact["is_primary"]:
                    role.append("primary")
                if contact["is_billing"]:
                    role.append("billing")
                role_str = f" ({', '.join(role)})" if role else ""
                print(f"  [CREATED] {contact['name_f']} {contact['name_l']} <{contact['email']}>{role_str}")
            else:
                print(f"  [ERROR] Failed to create {contact['email']}")

    # =========================================================================
    # CREATE TEST PROPOSAL (for new lead)
    # =========================================================================
    print("\n" + "=" * 60)
    print("CREATING TEST PROPOSAL")
    print("=" * 60)

    # New prospect - will create account/contact on sign
    PROSPECT_NAME_F = "Amanda"
    PROSPECT_NAME_L = "Foster"
    PROSPECT_COMPANY = "NorthStar Digital"
    PROSPECT_EMAIL = "benjaminjcrane+amanda@gmail.com"

    ITEMS = [
        {
            "name": "CRM Data Audit & Cleanup",
            "description": "Comprehensive audit of your CRM data including deduplication, field standardization, contact enrichment, and email validation. Deliverable: Clean, normalized CRM with detailed change log and data quality report.",
            "price": 4500.00,
        },
        {
            "name": "ICP Definition & TAM Analysis",
            "description": "Define your Ideal Customer Profile and build a Total Addressable Market analysis. Includes firmographic research, market sizing, and competitive landscape overview.",
            "price": 3500.00,
        },
        {
            "name": "Prospect List Build",
            "description": "Build a targeted prospect list based on your ICP. Includes 750+ qualified accounts with decision-maker contacts, verified emails, and CRM-ready import file.",
            "price": 5500.00,
        },
    ]

    TOTAL = sum(item["price"] for item in ITEMS)
    NOTES = "Payment terms: 50% due upon signing, 50% due upon completion. Work begins within 5 business days of signed agreement."

    proposal_data = {
        "org_id": ORG_ID,
        "client_email": PROSPECT_EMAIL,
        "client_name_f": PROSPECT_NAME_F,
        "client_name_l": PROSPECT_NAME_L,
        "client_company": PROSPECT_COMPANY,
        "status": 1,  # Sent - viewable on frontend
        "total": TOTAL,
        "notes": NOTES,
    }

    result = supabase.table("proposals").insert(proposal_data).execute()

    if not result.data:
        print("  [ERROR] Failed to create proposal")
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

    print(f"\n  Proposal ID: {proposal_id}")
    print(f"  Short ID:    {short_id}")
    print(f"\n  Prospect: {PROSPECT_NAME_F} {PROSPECT_NAME_L}")
    print(f"  Company:  {PROSPECT_COMPANY}")
    print(f"  Email:    {PROSPECT_EMAIL}")
    print(f"\n  Projects:")
    for item in ITEMS:
        print(f"    - {item['name']}: ${item['price']:,.2f}")
    print(f"\n  Total: ${TOTAL:,.2f}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"\n  Accounts created: {len(account_ids)}")
    print(f"  Contacts created: {len(contacts_data)}")
    print(f"  Proposal created: 1")

    print("\n  Test URLs:")
    print(f"    Proposal: https://revenueactivation.com/proposal/{short_id}")
    print(f"    API Accounts: http://localhost:8000/api/accounts")
    print(f"    API Contacts: http://localhost:8000/api/contacts")

    print("\n  Test the proposal signing flow:")
    print(f"    1. Visit https://revenueactivation.com/proposal/{short_id}")
    print(f"    2. Sign the proposal")
    print(f"    3. Check that account 'NorthStar Digital' was created")
    print(f"    4. Check that contact 'Amanda Foster' was created")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
