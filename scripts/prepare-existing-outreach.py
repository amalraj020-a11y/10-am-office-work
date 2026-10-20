"""Prepare a send-review queue for an already generated Ollama prospect."""
import json, re, sys, urllib.parse
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
businesses = json.loads((ROOT / "data" / "prospects.json").read_text(encoding="utf-8"))
name = sys.argv[1] if len(sys.argv) > 1 else "Mrs. Wilson's Cafe"
business = next(item for item in businesses if item["business_name"] == name)
slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
whatsapp = f"Hello {name} team. I prepared a simple website preview for your cafe using public business details. I can customize it, deploy it, and add backend features if you are interested, with a small budget agreed in advance. May I share the preview with you?"
email = f"Hello {name} team,\n\nI prepared a simple website preview for your cafe using the public business details we found. It is only a concept for your review. If you are interested, I can customize it, deploy it, and add backend features after confirming the exact requirements and a small budget.\n\nThank you."
preview = f"https://github.com/amalraj020-a11y/10-am-office-work/tree/main/sites/{slug}"
home_image = f"https://raw.githubusercontent.com/amalraj020-a11y/10-am-office-work/main/work/screenshots/{slug}-home.jpg"
services_image = f"https://raw.githubusercontent.com/amalraj020-a11y/10-am-office-work/main/work/screenshots/{slug}-services.jpg"
whatsapp = f"{whatsapp}\n\nWebsite preview: {preview}\n\nScreenshots: {home_image} and {services_image}\n\nIf you are interested, I can customize it, deploy it, and add backend features within a small agreed budget."
phone = re.sub(r"[^0-9]", "", business.get("phone", ""))
record = {
    "prospect_id": business["id"], "business_name": name, "model": "qwen3:4b",
    "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    "email": {"status": "draft_only", "subject": f"A website preview for {name}", "body": email},
    "whatsapp": {"status": "pending_user_send", "phone": business.get("phone", ""), "prefilled_url": f"https://wa.me/{phone}?text={urllib.parse.quote(whatsapp)}", "body": whatsapp, "attachments": ["work/screenshots/mrs-wilsons-cafe-home.jpg", "work/screenshots/mrs-wilsons-cafe-services.jpg"]},
    "note": "Qwen prepared this outreach. Sending requires a connected account/API and user approval.",
}
(ROOT / "outreach").mkdir(exist_ok=True)
(ROOT / "outreach" / f"{slug}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
(ROOT / "outreach" / "README.md").write_text("# Outreach queue\n\nEach JSON file contains Qwen-generated email and WhatsApp content. `pending_user_send` means the prefilled WhatsApp link is ready for review; the local Ollama process does not silently send external messages.\n", encoding="utf-8")
print(json.dumps({"business": name, "whatsapp_prefilled_url": record["whatsapp"]["prefilled_url"], "status": "pending_user_send"}))
