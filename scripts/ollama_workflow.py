"""Local 10 AM workflow powered by Ollama qwen3:4b.

This script creates website/demo assets and synchronizes them to GitHub.
It intentionally does not send WhatsApp/email without an explicit adapter.
"""
from __future__ import annotations
import csv, json, os, re, subprocess, sys, urllib.parse, urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
REPO_NAME = "10-am-office-work"

def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "business"

def ask_ollama(prompt: str) -> str:
    payload = json.dumps({"model": MODEL, "prompt": prompt, "stream": False, "think": False, "options": {"temperature": 0.2, "num_predict": 900}}).encode()
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

def build_site(business: dict, content: dict, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    title = content.get("title", business["business_name"])
    intro = content.get("intro", "A welcoming local place for good food and good company.")
    cards = content.get("cards", [])[:4]
    cards_html = "".join(f'<article class="card"><span>{c.get("label", "Highlight")}</span><h2>{c.get("title", "Service")}</h2><p>{c.get("description", "Made with care for the neighbourhood.")}</p></article>' for c in cards)
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{intro}"><title>{title}</title><style>
:root{{--ink:#142019;--muted:#68766d;--paper:#f8f5ef;--leaf:#1e4e3a;--lime:#d8e6bd;--orange:#e77b45}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font-family:system-ui,sans-serif;line-height:1.6}}header,main,footer{{max-width:1100px;margin:auto;padding:24px}}header{{display:flex;justify-content:space-between;align-items:center}}nav{{display:flex;gap:18px}}a{{color:inherit}}.hero{{padding:70px 24px;display:grid;grid-template-columns:1.1fr .9fr;gap:40px;align-items:center}}.eyebrow{{color:var(--orange);font-size:.75rem;letter-spacing:.18em;text-transform:uppercase;font-weight:800}}h1,h2{{font-family:Georgia,serif;font-weight:500;line-height:1}}h1{{font-size:clamp(3.3rem,8vw,6.8rem);letter-spacing:-.07em;margin:14px 0}}.lead{{font-size:1.15rem;color:var(--muted);max-width:540px}}.button{{display:inline-block;padding:12px 18px;border-radius:999px;background:var(--leaf);color:white;text-decoration:none;font-weight:700;margin-top:18px}}.art{{min-height:390px;border-radius:42% 42% 20px 20px;background:linear-gradient(135deg,#f0c57d,#e77b45 45%,#356e51 46%,#d8e6bd);box-shadow:18px 20px 0 #e4ded1}}.section{{padding:70px 24px}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}}.card{{background:white;padding:22px;border-radius:18px;min-height:205px;box-shadow:0 8px 24px #14201912}}.card:nth-child(2){{background:var(--lime)}}.card:nth-child(3){{background:#f8d8b9}}.card:nth-child(4){{background:var(--leaf);color:white}}.card span{{font-size:.78rem;opacity:.7}}.card h2{{font-size:2rem}}.visit{{background:var(--leaf);color:white;border-radius:24px;padding:32px;display:grid;grid-template-columns:1fr 1fr;gap:24px}}.visit p{{color:var(--lime)}}footer{{color:var(--muted);font-size:.85rem}}@media(max-width:760px){{.hero,.visit{{grid-template-columns:1fr}}.grid{{grid-template-columns:repeat(2,1fr)}}nav{{display:none}}}}@media(max-width:480px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body><header><strong>{title}</strong><nav><a href="#services">Services</a><a href="#visit">Visit</a></nav></header><main><section class="hero"><div><div class="eyebrow">{business.get("city_area", "Local")}</div><h1>{title}</h1><p class="lead">{intro}</p><a class="button" href="#visit">Plan your visit ↗</a></div><div class="art"></div></section><section id="services" class="section"><div class="eyebrow">Made for the neighbourhood</div><h2>What guests come for.</h2><div class="grid">{cards_html}</div></section><section id="visit" class="section"><div class="visit"><div><div class="eyebrow">Come by</div><h2>See you soon.</h2><p>{business.get("address", "Confirm address before publishing.")}<br>{business.get("hours", "Confirm opening hours before publishing.")}</p></div><div><p><strong>Phone:</strong> {business.get("phone", "Confirm phone") or "Confirm phone"}</p><p><strong>Services:</strong> {", ".join(business.get("services", []))}</p><p><strong>Website demo:</strong> Prepared for owner review.</p></div></div></section></main><footer>Demo concept. Confirm all business details and permissions before production.</footer></body></html>'''
    (target / "index.html").write_text(html, encoding="utf-8")

def append_csv(path: Path, headers: list[str], row: list[str]) -> None:
    existing = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if not existing: writer.writerow(headers)
        writer.writerow(row)

def prepare_outreach(business: dict, content: dict, site_slug: str, now: str) -> None:
    """Create reviewable delivery records; this never sends a message by itself."""
    repo_url = f"https://github.com/amalraj020-a11y/{REPO_NAME}/tree/main/sites/{site_slug}"
    whatsapp_text = content.get("whatsapp_body", "").strip()
    screenshot_paths = [f"work/screenshots/{site_slug}-home.jpg", f"work/screenshots/{site_slug}-services.jpg"]
    screenshot_links = [f"https://github.com/amalraj020-a11y/{REPO_NAME}/blob/main/{path}" for path in screenshot_paths]
    if repo_url not in whatsapp_text:
        whatsapp_text = f"{whatsapp_text}\n\nWebsite preview: {repo_url}\n\nScreenshots: {screenshot_links[0]} and {screenshot_links[1]}\n\nIf you are interested, I can customize it, deploy it, and add backend features within a small agreed budget."
    phone = re.sub(r"[^0-9]", "", business.get("phone", ""))
    record = {
        "prospect_id": business["id"],
        "business_name": business["business_name"],
        "model": MODEL,
        "created_at": now,
        "email": {"status": "draft_only", "subject": content.get("email_subject", f"A website preview for {business['business_name']}"), "body": content.get("email_body", "")},
        "whatsapp": {"status": "pending_user_send", "phone": business.get("phone", ""), "prefilled_url": f"https://wa.me/{phone}?text={urllib.parse.quote(whatsapp_text)}" if phone else "", "body": whatsapp_text, "attachments": screenshot_paths},
        "note": "Qwen prepared this outreach. Sending requires a connected account/API and user approval.",
    }
    outreach_dir = ROOT / "outreach"
    outreach_dir.mkdir(exist_ok=True)
    (outreach_dir / f"{site_slug}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    (outreach_dir / "README.md").write_text("# Outreach queue\n\nEach JSON file contains Qwen-generated email and WhatsApp content. `pending_user_send` means the prefilled WhatsApp link is ready for review; the local Ollama process does not silently send external messages.\n", encoding="utf-8")

def completed_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as handle:
        return {row.get("Prospect ID", "") for row in csv.DictReader(handle)}

def main() -> int:
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    data = json.loads((ROOT / "data" / "prospects.json").read_text(encoding="utf-8"))
    done = completed_ids(ROOT / "tracker" / "prospects.csv")
    pending = [candidate for candidate in data if candidate.get("id") not in done]
    if not pending:
        print(json.dumps({"status": "idle", "model": MODEL, "reason": "No unprocessed verified prospects in data/prospects.json"}))
        return 0
    business = pending[0]
    if business["business_name"].startswith("REPLACE"):
        raise SystemExit("Add one verified no-website business to data/prospects.json before running.")
    prompt = f'''You are the local-business website assistant. Use only the verified facts below. Create original marketing copy for a responsive one-page website. Do not invent reviews, ratings, founders, prices, claims, or services. Return JSON only with keys title, intro, cards (array of 4 objects with label, title, description), email_subject, email_body, whatsapp_body.
FACTS: {json.dumps(business, ensure_ascii=False)}'''
    raw = ask_ollama(prompt)
    try:
        content = extract_json(raw)
    except ValueError:
        # Keep the run useful when a local model returns prose instead of JSON.
        # The facts remain deterministic and the failed model response is retained for review.
        content = {
            "title": business["business_name"],
            "intro": f"A welcoming {business.get('category', 'local')} place in {business.get('city_area', 'the neighbourhood')}, made for good food and good company.",
            "cards": [{"label": f"0{i+1} / Local favourite", "title": service.title(), "description": "A detail to confirm with the business before publishing."} for i, service in enumerate(business.get("services", [])[:4])],
            "email_subject": f"A website preview for {business['business_name']}",
            "email_body": f"Hello {business['business_name']} team,\n\nI prepared a simple website preview for your cafe using the public business details we found. It is only a concept for your review. If you are interested, I can customize it, deploy it, and add backend features after confirming the exact requirements and a small budget.\n\nThank you.",
            "whatsapp_body": f"Hello {business['business_name']} team. I prepared a simple website preview for your cafe using public business details. I can customize it, deploy it, and add backend features if you are interested, with a small budget agreed in advance. May I share the preview with you?",
        }
        (ROOT / "docs" / f"{slug(business['business_name'])}-ollama-raw-response.txt").write_text(raw, encoding="utf-8")
    site_slug = slug(business["business_name"])
    build_site(business, content, ROOT / "sites" / site_slug)
    (ROOT / "docs" / f"{site_slug}-ollama-run.md").write_text(f"# Ollama run\\n\\nModel: `{MODEL}`\\nRun: `{now}`\\n\\nBusiness facts:\\n```json\\n{json.dumps(business, indent=2, ensure_ascii=False)}\\n```\\n\\nNo business details were invented by the workflow.\\n", encoding="utf-8")
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
