#!/usr/bin/env python3
"""Update Modern Full org with email notification settings."""

import os
from supabase import create_client


def main():
    ORG_ID = "9c187159-adc1-4cdd-af84-5c309d1ccdd8"

    supabase = create_client(
        os.environ["SERVICE_ENGINE_X_SUPABASE_URL"],
        os.environ["SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY"],
    )

    result = supabase.table("organizations").update({
        "domain": "modernfull.com",
        "notification_email": "ben@modernfull.com",
    }).eq("id", ORG_ID).execute()

    if result.data:
        print("Updated Modern Full org:")
        print(f"  domain: modernfull.com")
        print(f"  notification_email: ben@modernfull.com")
    else:
        print("ERROR: Failed to update org")


if __name__ == "__main__":
    main()
