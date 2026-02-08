#!/usr/bin/env python3
"""Generate API token for an organization."""

import os
import secrets
from hashlib import sha256
from datetime import datetime, timezone

from dotenv import load_dotenv
from supabase import create_client

# Load from parent .env.local (Next.js convention)
load_dotenv("../.env.local")

# Configuration
ORG_ID = "11111111-1111-1111-1111-111111111111"
USER_EMAIL = "team@revenueactivation.com"
TOKEN_NAME = "Customer Portal API Token"

def main():
    # Connect to Supabase
    supabase = create_client(
        os.environ.get("SUPABASE_URL") or os.environ["SERVICE_ENGINE_X_SUPABASE_URL"],
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ["SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY"]
    )

    # Find user by email
    user_result = supabase.table("users").select("id, email").eq("email", USER_EMAIL).execute()
    if not user_result.data:
        print(f"ERROR: User not found: {USER_EMAIL}")
        return

    user_id = user_result.data[0]["id"]
    print(f"Found user: {USER_EMAIL} (ID: {user_id})")

    # Generate random token (48 chars = 36 bytes base64-ish, very secure)
    plaintext_token = f"sengx_{secrets.token_urlsafe(36)}"

    # Hash the token
    token_hash = sha256(plaintext_token.encode()).hexdigest()

    # Insert into api_tokens
    result = supabase.table("api_tokens").insert({
        "user_id": user_id,
        "org_id": ORG_ID,
        "name": TOKEN_NAME,
        "token_hash": token_hash,
        "expires_at": None,
    }).execute()

    if result.data:
        record = result.data[0]
        print("\n" + "="*60)
        print("API TOKEN CREATED SUCCESSFULLY")
        print("="*60)
        print(f"\nDatabase Record:")
        print(f"  ID: {record['id']}")
        print(f"  Name: {record['name']}")
        print(f"  Org ID: {record['org_id']}")
        print(f"  User ID: {record['user_id']}")
        print(f"  Created: {record['created_at']}")
        print(f"  Expires: {record['expires_at'] or 'Never'}")
        print("\n" + "-"*60)
        print("PLAINTEXT TOKEN (save this - it cannot be recovered):")
        print("-"*60)
        print(f"\n{plaintext_token}\n")
        print("-"*60)
    else:
        print("ERROR: Failed to create token")

if __name__ == "__main__":
    main()
