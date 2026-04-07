#!/usr/bin/env python3
"""Create SecurityPal AI client for Revenue Activation."""

import os
from datetime import datetime, timezone

import bcrypt
from supabase import create_client


def main():
    # Revenue Activation org ID
    ORG_ID = "11111111-1111-1111-1111-111111111111"

    # Client details
    COMPANY_NAME = "SecurityPal AI"
    COMPANY_DOMAIN = "securitypalhq.com"
    CONTACT_FIRST = "Pukar"
    CONTACT_LAST = "Hamal"
    CONTACT_EMAIL = "benjaminjcrane+pukar@gmail.com"
    PASSWORD = "SecurityPal123!"

    supabase = create_client(
        os.environ["SERVICE_ENGINE_X_SUPABASE_URL"],
        os.environ["SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY"],
    )

    now = datetime.now(timezone.utc).isoformat()

    # =========================================================================
    # 1. CREATE ACCOUNT
    # =========================================================================
    print("\n" + "=" * 60)
    print("CREATING ACCOUNT")
    print("=" * 60)

    # Check if account already exists
    existing_account = (
        supabase.table("accounts")
        .select("id")
        .eq("org_id", ORG_ID)
        .eq("domain", COMPANY_DOMAIN)
        .execute()
    )

    if existing_account.data:
        account_id = existing_account.data[0]["id"]
        print(f"  [EXISTS] {COMPANY_NAME} ({account_id})")
    else:
        account_data = {
            "org_id": ORG_ID,
            "name": COMPANY_NAME,
            "domain": COMPANY_DOMAIN,
            "lifecycle": "lead",
            "source": "referral",
            "balance": 0.00,
            "total_spent": 0.00,
            "note": "AI-powered security questionnaire automation",
            "created_at": now,
            "updated_at": now,
        }
        result = supabase.table("accounts").insert(account_data).execute()
        if result.data:
            account_id = result.data[0]["id"]
            print(f"  [CREATED] {COMPANY_NAME} ({account_id})")
        else:
            print(f"  [ERROR] Failed to create account")
            return

    # =========================================================================
    # 2. CREATE CONTACT
    # =========================================================================
    print("\n" + "=" * 60)
    print("CREATING CONTACT")
    print("=" * 60)

    # Check if contact already exists
    existing_contact = (
        supabase.table("contacts")
        .select("id")
        .eq("org_id", ORG_ID)
        .eq("email", CONTACT_EMAIL)
        .execute()
    )

    if existing_contact.data:
        contact_id = existing_contact.data[0]["id"]
        print(f"  [EXISTS] {CONTACT_FIRST} {CONTACT_LAST} <{CONTACT_EMAIL}>")
    else:
        contact_data = {
            "org_id": ORG_ID,
            "account_id": account_id,
            "name_f": CONTACT_FIRST,
            "name_l": CONTACT_LAST,
            "email": CONTACT_EMAIL,
            "title": "Founder",
            "is_primary": True,
            "is_billing": True,
            "created_at": now,
            "updated_at": now,
        }
        result = supabase.table("contacts").insert(contact_data).execute()
        if result.data:
            contact_id = result.data[0]["id"]
            print(f"  [CREATED] {CONTACT_FIRST} {CONTACT_LAST} <{CONTACT_EMAIL}> (primary, billing)")
        else:
            print(f"  [ERROR] Failed to create contact")
            return

    # =========================================================================
    # 3. CREATE USER (for login)
    # =========================================================================
    print("\n" + "=" * 60)
    print("CREATING USER")
    print("=" * 60)

    # Find client role
    role_result = (
        supabase.table("roles").select("id, name").ilike("name", "%client%").execute()
    )
    if not role_result.data:
        print("  [ERROR] Client role not found")
        return

    client_role_id = role_result.data[0]["id"]

    # Check if user already exists
    existing_user = (
        supabase.table("users").select("id").eq("email", CONTACT_EMAIL).execute()
    )

    if existing_user.data:
        user_id = existing_user.data[0]["id"]
        print(f"  [EXISTS] {CONTACT_EMAIL} ({user_id})")
    else:
        # Hash password
        password_hash = bcrypt.hashpw(
            PASSWORD.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        user_data = {
            "org_id": ORG_ID,
            "email": CONTACT_EMAIL,
            "name_f": CONTACT_FIRST,
            "name_l": CONTACT_LAST,
            "company": COMPANY_NAME,
            "role_id": client_role_id,
            "password_hash": password_hash,
            "status": 1,  # Active
        }
        result = supabase.table("users").insert(user_data).execute()
        if result.data:
            user_id = result.data[0]["id"]
            print(f"  [CREATED] {CONTACT_EMAIL} ({user_id})")
        else:
            print(f"  [ERROR] Failed to create user")
            return

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 60)
    print("SECURITYPAL AI CLIENT CREATED")
    print("=" * 60)
    print(f"\n  Account: {COMPANY_NAME}")
    print(f"  Domain:  {COMPANY_DOMAIN}")
    print(f"  Account ID: {account_id}")
    print(f"\n  Contact: {CONTACT_FIRST} {CONTACT_LAST}")
    print(f"  Email:   {CONTACT_EMAIL}")
    print(f"  Contact ID: {contact_id}")
    print(f"\n  Login Credentials:")
    print(f"    Email:    {CONTACT_EMAIL}")
    print(f"    Password: {PASSWORD}")
    print(f"    User ID:  {user_id}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
