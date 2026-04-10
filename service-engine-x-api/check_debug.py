import os
from supabase import create_client

url = os.environ.get("SERVICE_ENGINE_X_SUPABASE_URL")
key = os.environ.get("SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Missing env vars")
    exit(1)

try:
    supabase = create_client(url, key)
    # Just check the builder attributes
    builder = supabase.table("organizations").insert({})
    print(f"Type: {type(builder)}")
    print(f"Has select: {'select' in dir(builder)}")
    print(f"Attributes: {dir(builder)}")
except Exception as e:
    print(f"Error: {e}")
