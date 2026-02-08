#!/usr/bin/env python3
"""Create engagement and projects for Acme Corporation."""

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

    # 1. Find the Acme Corp client (testclient@example.com)
    client_result = supabase.table("users").select("id, name_f, name_l, email, company").eq("email", "testclient@example.com").execute()

    if not client_result.data:
        print("ERROR: Acme Corp client not found")
        print("Listing available clients...")
        all_clients = supabase.table("users").select("id, email, company").eq("org_id", ORG_ID).limit(10).execute()
        for c in all_clients.data:
            print(f"  - {c['email']} ({c.get('company', 'N/A')})")
        return

    client = client_result.data[0]
    client_id = client["id"]
    print(f"Found client: {client['name_f']} {client['name_l']} - {client['company']}")
    print(f"Client ID: {client_id}")

    # 2. Check if engagement already exists for this client
    existing_engagement = supabase.table("engagements").select("id, name").eq("client_id", client_id).eq("name", "Acme Corp - Revenue Operations Buildout").execute()

    if existing_engagement.data:
        engagement_id = existing_engagement.data[0]["id"]
        print(f"\nEngagement already exists: {engagement_id}")
    else:
        # Create the engagement
        engagement_data = {
            "org_id": ORG_ID,
            "client_id": client_id,
            "name": "Acme Corp - Revenue Operations Buildout",
            "status": 1,  # Active
        }
        engagement_result = supabase.table("engagements").insert(engagement_data).execute()
        engagement_id = engagement_result.data[0]["id"]
        print(f"\nCreated engagement: {engagement_id}")

    # 3. Define the 3 projects
    projects_data = [
        {
            "engagement_id": engagement_id,
            "org_id": ORG_ID,
            "name": "CRM Data Cleaning",
            "description": "Full audit and cleanup of Salesforce CRM data. Includes deduplication of 15,000+ contact records, standardization of company names and job titles, enrichment of missing fields (phone, LinkedIn), and validation of email addresses. Deliverable: Clean, enriched CRM ready for outbound campaigns.",
            "status": 1,  # Active
            "phase": 3,   # Build (in progress)
        },
        {
            "engagement_id": engagement_id,
            "org_id": ORG_ID,
            "name": "Inbound Automation System",
            "description": "Design and implementation of automated inbound lead handling. Includes HubSpot form integration, lead scoring model, automated email sequences (5-touch nurture), Slack notifications for hot leads, and CRM sync. Deliverable: Fully automated inbound funnel processing 200+ leads/month.",
            "status": 1,  # Active
            "phase": 2,   # Setup
        },
        {
            "engagement_id": engagement_id,
            "org_id": ORG_ID,
            "name": "Pipeline Dashboards",
            "description": "Executive revenue dashboards in Looker Studio. Includes pipeline velocity metrics, conversion rates by stage, rep performance leaderboards, forecast vs. actual tracking, and weekly automated email reports to leadership. Deliverable: 3 dashboards with real-time Salesforce data.",
            "status": 1,  # Active
            "phase": 1,   # Kickoff
        },
    ]

    # 4. Check existing projects and create new ones
    existing_projects = supabase.table("projects").select("id, name").eq("engagement_id", engagement_id).execute()
    existing_names = {p["name"] for p in existing_projects.data}

    created_count = 0
    for project in projects_data:
        if project["name"] in existing_names:
            print(f"Project already exists: {project['name']}")
            continue

        result = supabase.table("projects").insert(project).execute()
        print(f"Created project: {project['name']} ({result.data[0]['id']})")
        created_count += 1

    # 5. Summary
    print("\n" + "="*70)
    print("ACME CORP ENGAGEMENT DATA CREATED")
    print("="*70)
    print(f"\nClient: {client['name_f']} {client['name_l']}")
    print(f"Company: {client['company']}")
    print(f"Email: {client['email']}")
    print(f"\nEngagement: Acme Corp - Revenue Operations Buildout")
    print(f"Engagement ID: {engagement_id}")
    print(f"Status: Active")
    print(f"\nProjects:")
    print(f"  1. CRM Data Cleaning")
    print(f"     Phase: Build (in progress)")
    print(f"     Scope: 15,000+ contacts, dedup, enrichment, validation")
    print(f"     Price: $7,500")
    print(f"")
    print(f"  2. Inbound Automation System")
    print(f"     Phase: Setup")
    print(f"     Scope: HubSpot integration, lead scoring, nurture sequences")
    print(f"     Price: $5,000")
    print(f"")
    print(f"  3. Pipeline Dashboards")
    print(f"     Phase: Kickoff")
    print(f"     Scope: 3 Looker Studio dashboards, real-time metrics")
    print(f"     Price: Included")
    print(f"\nTotal Engagement Value: $12,500")
    print("="*70)

if __name__ == "__main__":
    main()
