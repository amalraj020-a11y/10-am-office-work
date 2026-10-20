"""Local 10 AM workflow powered by Ollama qwen3:4b.

This script creates website/demo assets and synchronizes them to GitHub.
The 10 AM workflow authorizes routine outreach without per-run permission; a connected WhatsApp/email adapter must perform the send and record the result.
"""
from __future__ import annotations
import csv, json, os, re, shutil, subprocess, sys, urllib.parse, urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
REPO_NAME = "10-am-office-work"

def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "business"

def ask_ollama(prompt: str) -> str:
    payload = json.dumps({"model": MODEL, "prompt": prompt, "stream": False, "think": False, "format": "json", "options": {"temperature": 0.2, "num_predict": 420}}).encode()
    request = urllib.request.Request(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=300) as response:
        body = json.loads(response.read().decode())
    return body.get("response", "").strip()

def run(*args: str, cwd: Path = ROOT, check: bool = True) -> str:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if check and result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return (result.stdout or result.stderr).strip()

def extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError("Ollama did not return JSON")
    return json.loads(match.group(0))

def build_site_from_approved_template(business: dict, content: dict, target: Path) -> None:
    """Copy the approved ThemeWagon/Technext template and adapt only verified facts."""
    source = ROOT.parent / "feane-template"
    if not source.exists():
        raise RuntimeError("Fresh approved template checkout is missing; no previously used template or generic replacement is permitted.")
    shutil.copytree(source, target, dirs_exist_ok=True)
    index = target / "index.html"
    html = index.read_text(encoding="utf-8")
    business_name = business["business_name"]
    intro = content.get("intro", "A welcoming local place for good food and good company.")
    replacements = {
        "Feane": business_name,
        "A restaurant website template": intro,
        "FREEHTML5.co": "MultiMax",
        "freehtml5.co": "#",
        "2016": "2026",
        "ThemeWagon": "MultiMax",
        "https://themewagon.com/": "#",
    }
    for old, new in replacements.items():
        html = html.replace(old, new)
    footer = f"&copy; 2026 {business_name}. All rights reserved.<br><strong>Developed by MultiMax</strong>"
    html = re.sub(r"<p class=\"to-animate\">.*?</p>", f'<p class="to-animate">{footer}</p>', html, count=1, flags=re.S)
    index.write_text(html, encoding="utf-8")
    for unwanted in target.rglob(".DS_Store"):
        unwanted.unlink(missing_ok=True)
    for unwanted_name in (".git", "README.txt"):
        unwanted = target / unwanted_name
        if unwanted.is_dir():
            shutil.rmtree(unwanted)
        elif unwanted.exists():
            unwanted.unlink()

def append_csv(path: Path, headers: list[str], row: list[str]) -> None:
    existing = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if not existing: writer.writerow(headers)
        writer.writerow(row)

def prepare_outreach(business: dict, content: dict, site_slug: str, now: str) -> None:
    """Create the auto-send queue record; the connected adapter sends and reports the result."""
    repo_url = f"https://github.com/amalraj020-a11y/{REPO_NAME}/tree/main/sites/{site_slug}"
    live_url = f"https://amalraj020-a11y.github.io/{REPO_NAME}/sites/{site_slug}/"
    email_text = content.get("email_body", "").strip()
    whatsapp_text = content.get("whatsapp_body", "").strip()
    company_followup = "Hi, I’m Amala from MultiMax. MultiMax is a small web development company that creates affordable websites for local businesses. We found your shop and thought it looked great, but noticed it did not have a dedicated website, so we prepared a website concept for you. If you are interested, we can proceed and offer it at a low agreed budget. Tell me and I will send the website preview and full details."
    screenshot_paths = [f"work/screenshots/{site_slug}-home.jpg", f"work/screenshots/{site_slug}-services.jpg"]
    screenshot_links = [f"https://raw.githubusercontent.com/amalraj020-a11y/{REPO_NAME}/main/{path}" for path in screenshot_paths]
    if live_url not in whatsapp_text:
        whatsapp_text = f"{whatsapp_text}\n\nLive website preview: {live_url}\n\nGitHub source: {repo_url}\n\nScreenshots: {screenshot_links[0]} and {screenshot_links[1]}\n\nIf you are interested, I can customize it, deploy it, and add backend features within a small agreed budget."
    if company_followup not in whatsapp_text:
        whatsapp_text = f"{whatsapp_text}\n\n{company_followup}"
    if live_url not in email_text:
        email_text = f"{email_text}\n\nLive website preview: {live_url}\n\nGitHub source: {repo_url}\n\nScreenshots: {screenshot_links[0]} and {screenshot_links[1]}".strip()
    phone = re.sub(r"[^0-9]", "", business.get("phone", ""))
    record = {
        "prospect_id": business["id"],
        "business_name": business["business_name"],
        "model": MODEL,
        "created_at": now,
        "email": {"status": "draft_only", "subject": content.get("email_subject", f"A website preview for {business['business_name']}"), "body": email_text, "live_url": live_url},
        "whatsapp": {"status": "queued_for_auto_send", "phone": business.get("phone", ""), "prefilled_url": f"https://wa.me/{phone}?text={urllib.parse.quote(whatsapp_text)}" if phone else "", "body": whatsapp_text, "attachments": screenshot_paths, "live_url": live_url},
        "note": "Routine outreach is authorized by the 10 AM workflow without per-run permission. The connected adapter must send and record sent/delivered, unavailable, or failed status.",
    }
    outreach_dir = ROOT / "outreach"
    outreach_dir.mkdir(exist_ok=True)
    (outreach_dir / f"{site_slug}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    (outreach_dir / "README.md").write_text("# Outreach queue\n\nEach JSON file contains Qwen-generated email and WhatsApp content. `queued_for_auto_send` means the 10 AM workflow is authorized to send through the connected adapter without asking for per-run permission; the owner receives the exact result afterward. If no reliable phone number or email is found after searching public listings, record `owner_contact_required` and ask the owner in WhatsApp for a verified contact channel.\n", encoding="utf-8")

def completed_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as handle:
        return {row.get("Prospect ID", "") for row in csv.DictReader(handle)}

def has_contact_channel(candidate: dict) -> bool:
    """Only start a new outreach build when a public contact channel exists.

    A channel adapter can later mark ``whatsapp_available`` false after checking
    WhatsApp. The next run then skips that prospect and selects another business
    in the same niche when one is available.
    """
    if candidate.get("whatsapp_available") is False:
        return False
    return bool(re.sub(r"[^0-9]", "", candidate.get("phone", "")) or candidate.get("public_email", "").strip())

def main() -> int:
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    data = json.loads((ROOT / "data" / "prospects.json").read_text(encoding="utf-8"))
    template_catalog = json.loads((ROOT / "data" / "template-catalog.json").read_text(encoding="utf-8"))
    done = completed_ids(ROOT / "tracker" / "prospects.csv")
    force_id = os.getenv("OLLAMA_FORCE_PROSPECT_ID", "").strip()
    pending = [candidate for candidate in data if candidate.get("id") == force_id] if force_id else [candidate for candidate in data if candidate.get("id") not in done]
    contactable = [candidate for candidate in pending if has_contact_channel(candidate)]
    if not force_id:
        pending = contactable
    if not pending:
        print(json.dumps({"status": "global_research_required", "model": MODEL, "reason": "No contactable prospect in the current queue; the research step must search worldwide for another same-niche no-website prospect before reporting no work."}))
        return 0
    business = pending[0]
    if business["business_name"].startswith("REPLACE"):
        raise SystemExit("Add one verified no-website business to data/prospects.json before running.")
    prompt = f'''You are the local-business website assistant. Use only the verified facts below. You MUST select a reputable approved free template and return all four template fields. For this test, use ThemeWagon's free Foodee template from Technext: template_source="ThemeWagon free catalog / Technext GitHub", template_url="https://themewagon.com/themes/free-bootstrap-templates-restaurant-website-design-online-ordering/", template_name="Foodee", license_note="Free template source; confirm the source license before commercial delivery." The source is a design/code starting point only; do not copy another business identity. Create original marketing copy for a responsive one-page website. Do not invent reviews, ratings, founders, prices, claims, or services. Return JSON only with keys niche, template_source, template_url, template_name, license_note, title, intro, cards (array of 4 objects with label, title, description), email_subject, email_body, whatsapp_body.
FACTS: {json.dumps(business, ensure_ascii=False)}
TEMPLATE CATALOG: {json.dumps(template_catalog, ensure_ascii=False)}'''
    raw = ask_ollama(prompt)
    try:
        content = extract_json(raw)
    except ValueError:
        # Never fall back to the retired generic layout. Preserve the model output
        # for diagnosis and stop so the next run can retry with an approved template.
        (ROOT / "docs" / f"{slug(business['business_name'])}-ollama-raw-response.txt").write_text(raw, encoding="utf-8")
        raise RuntimeError("Qwen did not return valid JSON; no website was created because the retired generic template is prohibited.")
    # Keep the model responsible for the copy, while pinning the build to the
    # approved source when Qwen omits metadata in an otherwise usable response.
    content.setdefault("template_source", "ThemeWagon free catalog / Technext GitHub")
    content.setdefault("template_url", "https://themewagon.com/themes/free-bootstrap-templates-restaurant-website-design-online-ordering/")
    content.setdefault("template_name", "Foodee")
    content.setdefault("license_note", "Free template source; confirm the source license before commercial delivery.")
    required_template = str(content.get("template_url", "")).strip()
    required_name = str(content.get("template_name", "")).strip()
    required_license = str(content.get("license_note", "")).strip()
    if not required_template or not required_name or not required_license or content.get("template_source") == "Retired legacy run; not approved for future builds":
        raise RuntimeError("Approved template source, name, URL, and license note are required; no website was created.")
    used_path = ROOT / "data" / "used-templates.json"
    used_templates = json.loads(used_path.read_text(encoding="utf-8")) if used_path.exists() else {}
    prior_users = used_templates.get(required_name, {}).get("used_for", [])
    if prior_users and business["business_name"] not in prior_users:
        raise RuntimeError(f"Template {required_name} was already used for another prospect; Qwen must select a fresh ThemeWagon template.")
    site_slug = slug(business["business_name"])
    build_site_from_approved_template(business, content, ROOT / "sites" / site_slug)
    used_templates.setdefault(required_name, {"source": content.get("template_source", ""), "url": required_template, "used_for": []})
    if business["business_name"] not in used_templates[required_name]["used_for"]:
        used_templates[required_name]["used_for"].append(business["business_name"])
    used_path.write_text(json.dumps(used_templates, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / "docs" / f"{site_slug}-ollama-run.md").write_text(f"# Ollama run\\n\\nModel: `{MODEL}`\\nRun: `{now}`\\n\\nNiche: `{content.get('niche', business.get('category', 'local business'))}`\\nTemplate source: `{content.get('template_source', 'Approved template required')}`\\nTemplate URL: `{content.get('template_url', '')}`\\nTemplate name: `{content.get('template_name', '')}`\\nLicense note: {content.get('license_note', 'Confirm before commercial delivery.')}\\n\\nBusiness facts:\\n```json\\n{json.dumps(business, indent=2, ensure_ascii=False)}\\n```\\n\\nNo business details were invented by the workflow.\\n", encoding="utf-8")
    (ROOT / "messages" / f"{site_slug}-ollama-email.md").write_text(content.get("email_body", ""), encoding="utf-8")
    (ROOT / "messages" / f"{site_slug}-ollama-whatsapp.md").write_text(content.get("whatsapp_body", ""), encoding="utf-8")
    prepare_outreach(business, content, site_slug, now)
    append_csv(ROOT / "tracker" / "prospects.csv", ["Prospect ID","Business name","Category","City / area","Phone","Email / contact","Google / Maps URL","Social URL","Official website checked","Qualification","Evidence / notes","Research date","Owner","Next action"], [business["id"],business["business_name"],business.get("category",""),business.get("city_area",""),business.get("phone",""),business.get("public_email",""),"",business.get("social_url",""),"No dedicated official website found","Qualified",business.get("website_evidence",""),now[:10],"Ollama","Review generated demo and verify outreach channel"])
    append_csv(ROOT / "tracker" / "delivery.csv", ["Prospect ID","Business name","Git repo","Code path / commit","Vercel project / preview","Demo screenshot path","Proposed price","Delivery status","Payment status","Deployment status","Owner approval","Notes"], [business["id"],business["business_name"],REPO_NAME,f"sites/{site_slug}/index.html","Not deployed","Not created","To propose","Demo ready","Not requested","Not deployed","Required",f"Generated with {MODEL}; outreach adapters are not configured."])
    run("git","add","sites", "docs", "messages", "tracker", "outreach")
    run("git","commit","-m",f"Generate {business['business_name']} demo with Ollama",check=False)
    run("git","push",check=False)
    print(json.dumps({"model":MODEL,"business":business["business_name"],"site":f"sites/{site_slug}/index.html","timestamp":now}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
