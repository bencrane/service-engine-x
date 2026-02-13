#!/usr/bin/env python3
"""Save OpenAPI specification to openapi.json file."""

import json
import os

# Set dummy env vars for OpenAPI generation (no DB connection needed)
os.environ.setdefault("SUPABASE_URL", "https://placeholder.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "placeholder")

from app.main import app

if __name__ == "__main__":
    spec = app.openapi()
    with open("openapi.json", "w") as f:
        json.dump(spec, f, indent=2)
    print(f"OpenAPI spec saved to openapi.json ({len(json.dumps(spec))} bytes)")
