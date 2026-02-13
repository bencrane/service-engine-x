#!/usr/bin/env python3
"""Create test data for customer portal."""

import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client

# Load from parent .env.local
load_dotenv("../.env.local")

ORG_ID = "11111111-1111-1111-1111-111111111111"

def main():
    supabase = create_client(
        os.environ.get("SUPABASE_URL") or os.environ["SERVICE_ENGINE_X_SUPABASE_URL"],
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ["SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY"]
    )

    # 1. Find client role (roles table is global, not per-org)
    role_result = supabase.table("roles").select("id, name").ilike("name", "%client%").execute()
    if not role_result.data:
        # Try to find any role
        all_roles = supabase.table("roles").select("id, name").execute()
        print("Available roles:")
        for r in all_roles.data:
            print(f"  - {r['name']} ({r['id']})")
        print("ERROR: Client role not found")
        return
    client_role_id = role_result.data[0]["id"]
    print(f"Found client role: {role_result.data[0]['name']} ({client_role_id})")

    # 2. Find "CRM Data Cleaning (One-Time)" service
    service_result = supabase.table("services").select("id, name, price").eq("org_id", ORG_ID).ilike("name", "%CRM Data Cleaning%").execute()
    if not service_result.data:
        print("ERROR: CRM Data Cleaning service not found")
        # List available services
        all_services = supabase.table("services").select("id, name").eq("org_id", ORG_ID).execute()
        print("Available services:")
        for s in all_services.data:
            print(f"  - {s['name']} ({s['id']})")
        return
    service = service_result.data[0]
    print(f"Found service: {service['name']} (${service['price']})")

    # 3. Create test client user
    client_data = {
        "org_id": ORG_ID,
        "email": "testclient@example.com",
        "name_f": "John",
        "name_l": "Doe",
        "company": "Acme Corp",
        "role_id": client_role_id,
        "password_hash": "test_client_no_login",  # Placeholder - client uses magic links
        "phone": "555-123-4567",
    }

    # Check if user already exists
    existing = supabase.table("users").select("id").eq("email", "testclient@example.com").execute()
    if existing.data:
        client_id = existing.data[0]["id"]
        print(f"Client already exists: {client_id}")
    else:
        client_result = supabase.table("users").insert(client_data).execute()
        client_id = client_result.data[0]["id"]
        print(f"Created client: {client_id}")

    # 4. Create test order
    import random
    import string
    order_number = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

    order_data = {
        "org_id": ORG_ID,
        "number": order_number,
        "user_id": client_id,
        "service_id": service["id"],
        "service_name": service["name"],
        "price": "5000.00",
        "currency": "USD",
        "quantity": 1,
        "status": 1,  # In Progress
        "note": "Initial CRM cleanup project",
        "form_data": {},
        "metadata": {},
    }
    order_result = supabase.table("orders").insert(order_data).execute()
    order = order_result.data[0]
    order_id = order["id"]
    print(f"Created order: {order_id}")

    # 5. Create tasks (is_complete = True for done, False for pending/in-progress)
    tasks = [
        {"name": "Connect to CRM API", "is_complete": True, "sort_order": 0, "description": "Set up API connection to client's CRM"},
        {"name": "Run data cleaning scripts", "is_complete": False, "sort_order": 1, "description": "Process and clean the CRM data"},
        {"name": "Deliver cleaned data", "is_complete": False, "sort_order": 2, "description": "Export and deliver the cleaned dataset"},
    ]
    for task in tasks:
        task["org_id"] = ORG_ID
        task["order_id"] = order_id
        task["is_public"] = True
        task["for_client"] = False

    tasks_result = supabase.table("order_tasks").insert(tasks).execute()
    print(f"Created {len(tasks_result.data)} tasks")

    # 6. Find a staff user for the reply message
    staff_result = supabase.table("users").select("id, email").eq("org_id", ORG_ID).eq("email", "team@revenueactivation.com").execute()
    staff_id = staff_result.data[0]["id"] if staff_result.data else client_id

    # 7. Create messages
    messages = [
        {
            "org_id": ORG_ID,
            "order_id": order_id,
            "user_id": client_id,
            "message": "When can I expect the cleaned data?",
            "staff_only": False,
        },
        {
            "org_id": ORG_ID,
            "order_id": order_id,
            "user_id": staff_id,
            "message": "Working on it now, should be ready by Friday!",
            "staff_only": False,
        },
    ]
    messages_result = supabase.table("order_messages").insert(messages).execute()
    print(f"Created {len(messages_result.data)} messages")

    # Summary
    print("\n" + "="*60)
    print("TEST DATA CREATED SUCCESSFULLY")
    print("="*60)
    print(f"\nClient: John Doe (testclient@example.com)")
    print(f"Client ID: {client_id}")
    print(f"\nOrder ID: {order_id}")
    print(f"Service: {service['name']}")
    print(f"Total: $5,000")
    print(f"Status: In Progress")
    print(f"\nTasks:")
    print(f"  ✓ Connect to CRM API (completed)")
    print(f"  → Run data cleaning scripts (in progress)")
    print(f"  ○ Deliver cleaned data (pending)")
    print(f"\nMessages: 2")
    print(f"\nTest URL: /orders/{order_id}")
    print("="*60)

if __name__ == "__main__":
    main()
