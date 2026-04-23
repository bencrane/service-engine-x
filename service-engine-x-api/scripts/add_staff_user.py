#!/usr/bin/env python3
"""Create a staff user. Prefers the same role as existing staff in the org."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone

import bcrypt
from supabase import create_client


def resolve_staff_role_id(supabase, org_id: str) -> tuple[str, str]:
    """Return (role_id, source_description)."""
    users = (
        supabase.table("users")
        .select("role_id")
        .eq("org_id", org_id)
        .limit(80)
        .execute()
    )
    role_ids = list({u["role_id"] for u in (users.data or []) if u.get("role_id")})
    if role_ids:
        roles = (
            supabase.table("roles")
            .select("id, name, dashboard_access")
            .in_("id", role_ids)
            .execute()
        )
        staff = [r for r in (roles.data or []) if r.get("dashboard_access", 0) > 0]
        if staff:
            staff.sort(key=lambda x: x["dashboard_access"], reverse=True)
            chosen = staff[0]
            return chosen["id"], f"same org as role '{chosen.get('name')}' (dashboard_access={chosen.get('dashboard_access')})"

    role_result = (
        supabase.table("roles")
        .select("id, name, dashboard_access")
        .gt("dashboard_access", 0)
        .order("dashboard_access", desc=True)
        .limit(1)
        .execute()
    )
    if not role_result.data:
        raise SystemExit("No staff role found: add roles or seed the roles table.")
    r = role_result.data[0]
    return r["id"], f"fallback global '{r.get('name')}' (dashboard_access={r.get('dashboard_access')})"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--org-id",
        default=os.environ.get("ADD_USER_ORG_ID", "22222222-2222-2222-2222-222222222222"),
    )
    parser.add_argument(
        "--email",
        default=os.environ.get("ADD_USER_EMAIL", "benjamin.crane@outboundsolutions.com"),
    )
    parser.add_argument("--first", default="Benjamin")
    parser.add_argument("--last", default="Crane")
    parser.add_argument("--company", default="Outbound Solutions")
    parser.add_argument(
        "--password",
        default=os.environ.get("ADD_USER_PASSWORD"),
        help="Required unless ADD_USER_PASSWORD is set",
    )
    args = parser.parse_args()
    if not args.password:
        print("Pass --password or set ADD_USER_PASSWORD", file=sys.stderr)
        sys.exit(1)

    url = os.environ.get("SERVICE_ENGINE_X_SUPABASE_URL")
    key = os.environ.get("SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        print(
            "Missing SERVICE_ENGINE_X_SUPABASE_URL or SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY",
            file=sys.stderr,
        )
        sys.exit(1)

    supabase = create_client(url, key)

    existing = supabase.table("users").select("id, org_id").eq("email", args.email).execute()
    if existing.data:
        print(f"User already exists: {args.email} -> {existing.data[0]['id']}")
        sys.exit(0)

    role_id, role_source = resolve_staff_role_id(supabase, args.org_id)
    print(f"Using role_id {role_id} ({role_source})")

    password_hash = bcrypt.hashpw(args.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    now = datetime.now(timezone.utc).isoformat()

    user_data = {
        "org_id": args.org_id,
        "email": args.email,
        "name_f": args.first,
        "name_l": args.last,
        "company": args.company,
        "role_id": role_id,
        "password_hash": password_hash,
        "status": 1,
        "created_at": now,
    }

    result = supabase.table("users").insert(user_data).execute()
    if not result.data:
        print("Insert failed (no row returned)", file=sys.stderr)
        sys.exit(1)

    uid = result.data[0]["id"]
    print(f"Created staff user {args.email} id={uid}")
    print("Change the password after first login if this was a one-off test password.")


if __name__ == "__main__":
    main()
