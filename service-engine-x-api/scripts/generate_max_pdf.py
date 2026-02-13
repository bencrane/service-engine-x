#!/usr/bin/env python3
"""Generate pre-filled PDF for Max Hirsch proposal."""

import os
from dotenv import load_dotenv
import docraptor
from supabase import create_client

load_dotenv("../.env.local")

# Max's details
FIRST_NAME = "Max"
LAST_NAME = "Hirsch"
EMAIL = "maxhirsch15@gmail.com"
COMPANY = "Uraiv, LLC"

# Proposal details
PROPOSAL_ID = "e30c2203-2403-4448-bef1-edcfd92c7879"
ORG_ID = "9c187159-adc1-4cdd-af84-5c309d1ccdd8"

HTML_CONTENT = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Service Agreement - {COMPANY}</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@500&family=Fraunces:wght@600;700&display=swap" rel="stylesheet">
<style>
  @page {{ size: letter; margin: 0.5in; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #0a0a0a;
    color: #e8e8e8;
    padding: 40px;
    line-height: 1.6;
    font-size: 11pt;
  }}
  .page {{ max-width: 640px; margin: 0 auto; }}
  .header {{ text-align: center; padding-bottom: 30px; border-bottom: 1px solid #1e1e1e; margin-bottom: 30px; }}
  .header h1 {{ font-family: 'Fraunces', serif; font-size: 24pt; font-weight: 700; margin-bottom: 8px; color: #fff; }}
  .header .subtitle {{ font-family: 'Fraunces', serif; font-size: 14pt; color: #777; font-style: italic; margin-bottom: 4px; }}
  .header .type {{ color: #777; font-size: 12pt; }}
  .price-tag {{ display: inline-block; margin-top: 16px; background: #141414; border: 1px solid #1e1e1e; padding: 10px 24px; border-radius: 50px; }}
  .price-tag .amount {{ font-family: 'JetBrains Mono', monospace; font-size: 28pt; font-weight: 500; }}
  .price-tag .label {{ font-size: 11pt; color: #777; margin-left: 8px; }}
  .section {{ margin-bottom: 28px; }}
  .section-label {{ font-size: 9pt; text-transform: uppercase; letter-spacing: 1.5px; color: #555; font-weight: 600; margin-bottom: 12px; }}
  .overview {{ font-size: 11pt; color: #777; line-height: 1.7; }}
  .overview strong {{ color: #e8e8e8; font-weight: 600; }}
  .card {{ background: #141414; border: 1px solid #1e1e1e; border-radius: 12px; padding: 20px; margin-bottom: 12px; }}
  .card-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }}
  .card-icon {{ width: 28px; height: 28px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 14px; }}
  .card-icon.purple {{ background: rgba(108,58,237,0.15); }}
  .card-icon.orange {{ background: rgba(245,158,11,0.15); }}
  .card-title {{ font-family: 'Fraunces', serif; font-size: 14pt; font-weight: 700; }}
  .card-desc {{ font-size: 10pt; color: #777; margin-bottom: 14px; line-height: 1.5; }}
  .deliverable {{ display: flex; gap: 8px; padding: 6px 0; font-size: 10pt; color: #777; border-bottom: 1px solid rgba(255,255,255,0.03); }}
  .deliverable:last-child {{ border-bottom: none; }}
  .deliverable .check {{ color: #22c55e; font-size: 12pt; min-width: 16px; }}
  .deliverable strong {{ color: #e8e8e8; font-weight: 500; }}
  .deliverable .desc {{ font-size: 9pt; color: #555; display: block; margin-top: 2px; }}
  .or-divider {{ display: flex; align-items: center; gap: 12px; margin: 20px 0; }}
  .or-divider .line {{ flex: 1; height: 1px; background: #1e1e1e; }}
  .or-divider span {{ font-size: 10pt; color: #555; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; }}
  .disclosure {{ font-size: 9pt; color: #555; line-height: 1.6; }}
  .sig-section {{ margin-top: 30px; padding-top: 24px; border-top: 1px solid #1e1e1e; }}
  .sig-card {{ background: #141414; border: 1px solid #1e1e1e; border-radius: 12px; padding: 20px; margin-bottom: 12px; }}
  .sig-label {{ font-size: 9pt; text-transform: uppercase; letter-spacing: 1.5px; color: #555; font-weight: 600; margin-bottom: 8px; }}
  .sig-info {{ margin-bottom: 12px; }}
  .sig-info-row {{ display: flex; gap: 12px; margin-bottom: 8px; }}
  .sig-info-item {{ flex: 1; background: rgba(255,255,255,0.03); border: 1px solid #1e1e1e; border-radius: 8px; padding: 10px 12px; font-size: 11pt; }}
  .sig-info-item.full {{ flex: none; width: 100%; }}
  .sig-box {{ border: 1px solid #1e1e1e; border-radius: 8px; height: 80px; background: #0a0a0a; display: flex; align-items: center; justify-content: center; }}
  .sig-placeholder {{ color: #555; font-size: 11pt; font-style: italic; }}
  .footer {{ text-align: center; font-size: 10pt; color: #555; margin-top: 20px; }}
</style>
</head>
<body>
<div class="page">
  <div class="header">
    <h1>Custom Automation System<br>Design, Build &amp; Deployment</h1>
    <p class="subtitle">Prepared for {COMPANY}</p>
    <p class="type">Service Agreement</p>
    <div class="price-tag">
      <span class="amount">$4,000</span>
      <span class="label">one-time</span>
    </div>
  </div>

  <div class="section">
    <div class="section-label">Overview</div>
    <p class="overview">
      This agreement covers the <strong>full design, build, and installation</strong> of one automation system. The client is granted the option to select either system outlined below within 90 days of purchase. Payment of $4,000 must be made on or before February 12th, 2026 via Zelle.<br><br>
      System architecture, tooling, and configuration are determined by the provider based on the client's business goals. Upon completion, the system will either be transferred to the client or hosted on the provider's infrastructure for up to one year. 30 days of priority support is included post-installation.
    </p>
  </div>

  <div class="section">
    <div class="card">
      <div class="card-header">
        <div class="card-icon purple">&#128232;</div>
        <div class="card-title">Outbound Sales System</div>
      </div>
      <p class="card-desc">A fully built outbound email infrastructure - from lead sourcing through campaign execution. Everything is configured and ready to send.</p>
      <div class="deliverable"><span class="check">&#10003;</span><span><strong>Targeted lead list</strong><span class="desc">Up to 5,000 contacts, sourced and verified against an ideal customer profile.</span></span></div>
      <div class="deliverable"><span class="check">&#10003;</span><span><strong>Email sending system</strong><span class="desc">Dedicated mailboxes set up and warmed, configured for deliverability.</span></span></div>
      <div class="deliverable"><span class="check">&#10003;</span><span><strong>Full end-to-end email campaigns</strong><span class="desc">Multi-step email sequences written, tested, and loaded.</span></span></div>
      <div class="deliverable"><span class="check">&#10003;</span><span><strong>Sending automation</strong><span class="desc">Scheduling, throttling, and sequencing configured end-to-end.</span></span></div>
      <div class="deliverable"><span class="check">&#10003;</span><span><strong>AI reply handling</strong><span class="desc">Positive reply detection and routing so no warm lead is missed.</span></span></div>
      <div class="deliverable"><span class="check">&#10003;</span><span><strong>$300 in Google AI Studio credits</strong><span class="desc">Set up on your behalf to cover initial infrastructure and API usage.</span></span></div>
      <div class="deliverable"><span class="check">&#10003;</span><span><strong>Deliverability optimization</strong><span class="desc">DNS records, SPF, DKIM, DMARC all configured for maximum inbox placement.</span></span></div>
    </div>

    <div class="or-divider">
      <div class="line"></div>
      <span>or</span>
      <div class="line"></div>
    </div>

    <div class="card">
      <div class="card-header">
        <div class="card-icon orange">&#127916;</div>
        <div class="card-title">AI Ad Content Generation System</div>
      </div>
      <p class="card-desc">An automated system that produces hyper-realistic AI-generated "UGC-style" video and image ad content - no creators, no shoots, no scheduling.</p>
      <div class="deliverable"><span class="check">&#10003;</span><span><strong>AI avatar setup</strong><span class="desc">Realistic digital presenters generated for each product video.</span></span></div>
      <div class="deliverable"><span class="check">&#10003;</span><span><strong>Script generation pipeline</strong><span class="desc">AI agent generates optimized prompts tailored to each product.</span></span></div>
      <div class="deliverable"><span class="check">&#10003;</span><span><strong>Video production automation</strong><span class="desc">End-to-end pipeline from product details to finished video, with multiple AI model support.</span></span></div>
      <div class="deliverable"><span class="check">&#10003;</span><span><strong>Management dashboard</strong><span class="desc">A dedicated interface to manage product details, trigger generation, and track output status.</span></span></div>
      <div class="deliverable"><span class="check">&#10003;</span><span><strong>Automated status tracking</strong><span class="desc">Real-time generation status and video delivery updated directly in the sheet.</span></span></div>
      <div class="deliverable"><span class="check">&#10003;</span><span><strong>$300 in Google AI Studio credits</strong><span class="desc">Set up on your behalf to cover initial AI generation and API usage.</span></span></div>
    </div>
  </div>

  <div class="section">
    <div class="section-label">Disclosure</div>
    <p class="disclosure">
      Deliverables listed above represent the intended scope and may be adjusted by the provider based on technical feasibility and platform availability. The final system may differ from what is described. Additional 3rd-party platform or API usage will be incurred by the client directly (e.g. Google Gemini, OpenAI, SmartLead).
    </p>
  </div>

  <div class="sig-section">
    <div class="section-label">Signature</div>

    <div class="sig-card">
      <div class="sig-label">Signer Details</div>
      <div class="sig-info">
        <div class="sig-info-row">
          <div class="sig-info-item">{FIRST_NAME}</div>
          <div class="sig-info-item">{LAST_NAME}</div>
        </div>
        <div class="sig-info-item full">{EMAIL}</div>
      </div>
    </div>

    <div class="sig-card">
      <div class="sig-label">Agreement Accepted</div>
      <div class="sig-box" style="text-align: center; padding: 20px;">
        <div style="color: #22c55e; font-size: 13pt; margin-bottom: 8px;">&#10003; Electronically signed by {FIRST_NAME} {LAST_NAME}</div>
        <div style="color: #555; font-size: 9pt;">February 12, 2026</div>
      </div>
    </div>
  </div>
</div>
</body>
</html>
"""


def main():
    # DocRaptor API key
    docraptor_key = os.environ.get("DOCRAPTOR_API_KEY", "oUcqyfynOYOBkEIV8_IU")

    print("Generating PDF with DocRaptor...")

    doc_api = docraptor.DocApi()
    doc_api.api_client.configuration.username = docraptor_key

    try:
        pdf_bytes = doc_api.create_doc({
            "test": False,
            "document_type": "pdf",
            "document_content": HTML_CONTENT,
            "name": f"proposal-{PROPOSAL_ID[:8]}.pdf",
        })
        print(f"PDF generated: {len(pdf_bytes)} bytes")
    except Exception as e:
        print(f"DocRaptor error: {e}")
        return

    # Upload to Supabase Storage
    print("Uploading to Supabase Storage...")

    supabase = create_client(
        os.environ.get("SUPABASE_URL") or os.environ["SERVICE_ENGINE_X_SUPABASE_URL"],
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ["SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY"],
    )

    storage_path = f"{ORG_ID}/{PROPOSAL_ID}.pdf"

    try:
        # Delete existing if any
        supabase.storage.from_("proposals").remove([storage_path])
    except:
        pass

    result = supabase.storage.from_("proposals").upload(
        storage_path,
        pdf_bytes,
        {"content-type": "application/pdf"}
    )

    # Get public URL
    pdf_url = supabase.storage.from_("proposals").get_public_url(storage_path)
    print(f"Uploaded to: {pdf_url}")

    # Update proposal record
    print("Updating proposal record...")

    supabase.table("proposals").update({
        "pdf_url": pdf_url,
        "client_name_f": FIRST_NAME,
        "client_name_l": LAST_NAME,
        "client_email": EMAIL,
    }).eq("id", PROPOSAL_ID).execute()

    print("\n" + "=" * 60)
    print("PDF CREATED SUCCESSFULLY")
    print("=" * 60)
    print(f"PDF URL: {pdf_url}")
    print(f"Proposal ID: {PROPOSAL_ID[:8]}")
    print(f"Client: {FIRST_NAME} {LAST_NAME} <{EMAIL}>")
    print("=" * 60)


if __name__ == "__main__":
    main()
