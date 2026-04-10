import os
from supabase import create_client

url = os.environ.get("SERVICE_ENGINE_X_SUPABASE_URL")
key = os.environ.get("SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Missing env vars")
    exit(1)

try:
    supabase = create_client(url, key)
    # Check help for insert
    help(supabase.table("organizations").insert)
except Exception as e:
    print(f"Error: {e}")
