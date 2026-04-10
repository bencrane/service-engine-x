import os
from supabase import create_client

url = os.environ.get("SERVICE_ENGINE_X_SUPABASE_URL")
key = os.environ.get("SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Missing env vars")
    exit(1)

try:
    supabase = create_client(url, key)
    org_id = "11111111-1111-1111-1111-111111111111"
    response = supabase.table("organizations").select("*").eq("id", org_id).execute()
    print(response.data)
except Exception as e:
    print(f"Error: {e}")
