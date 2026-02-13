#!/usr/bin/env python3
"""Create a new organization with admin user."""

import os
import uuid
import bcrypt
from dotenv import load_dotenv
from supabase import create_client

# Load environment
load_dotenv("../.env.local")


def main():
    # Organization details
    ORG_NAME = "Modern Full"
    ORG_SLUG = "modern-full"
    ADMIN_EMAIL = "billing@modernfull.com"
    ADMIN_PASSWORD = "ChangeMe123!"  # User should change this after first login

    supabase = create_client(
        os.environ.get("SUPABASE_URL") or os.environ["SERVICE_ENGINE_X_SUPABASE_URL"],
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ["SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY"],
    )

    # 1. Check if organization already exists
    existing_org = (
        supabase.table("organizations").select("id").eq("slug", ORG_SLUG).execute()
    )
    if existing_org.data:
        print(f"Organization '{ORG_SLUG}' already exists: {existing_org.data[0]['id']}")
        org_id = existing_org.data[0]["id"]
    else:
        # Create organization
        org_data = {
            "name": ORG_NAME,
            "slug": ORG_SLUG,
        }
        org_result = supabase.table("organizations").insert(org_data).execute()
        org_id = org_result.data[0]["id"]
        print(f"Created organization: {ORG_NAME} ({org_id})")

    # 2. Find admin role (dashboard_access > 0, highest access)
    role_result = (
        supabase.table("roles")
        .select("id, name, dashboard_access")
        .gt("dashboard_access", 0)
        .order("dashboard_access", desc=True)
        .limit(1)
        .execute()
    )
    if not role_result.data:
        print("ERROR: No admin role found. Listing all roles:")
        all_roles = supabase.table("roles").select("id, name, dashboard_access").execute()
        for r in all_roles.data:
            print(f"  - {r['name']} (dashboard_access={r['dashboard_access']})")
        return

    admin_role = role_result.data[0]
    print(f"Using role: {admin_role['name']} (dashboard_access={admin_role['dashboard_access']})")

    # 3. Check if admin user already exists
    existing_user = (
        supabase.table("users").select("id").eq("email", ADMIN_EMAIL).execute()
    )
    if existing_user.data:
        print(f"Admin user already exists: {existing_user.data[0]['id']}")
        user_id = existing_user.data[0]["id"]
    else:
        # Hash password
        password_hash = bcrypt.hashpw(
            ADMIN_PASSWORD.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # Create admin user
        user_data = {
            "org_id": org_id,
            "email": ADMIN_EMAIL,
            "name_f": "Benjamin",
            "name_l": "Crane",
            "role_id": admin_role["id"],
            "password_hash": password_hash,
            "status": 1,  # Active
        }
        user_result = supabase.table("users").insert(user_data).execute()
        user_id = user_result.data[0]["id"]
        print(f"Created admin user: {ADMIN_EMAIL} ({user_id})")

    # Summary
    print("\n" + "=" * 60)
    print("ORGANIZATION CREATED SUCCESSFULLY")
    print("=" * 60)
    print(f"\nOrganization: {ORG_NAME}")
    print(f"Org ID: {org_id}")
    print(f"Slug: {ORG_SLUG}")
    print(f"\nAdmin Email: {ADMIN_EMAIL}")
    print(f"Admin Password: {ADMIN_PASSWORD}")
    print(f"User ID: {user_id}")
    print("\n⚠️  Remember to change the password after first login!")
    print("=" * 60)


if __name__ == "__main__":
    main()
