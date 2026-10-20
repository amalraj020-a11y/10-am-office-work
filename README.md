# 10 AM Office Work

Amala's 10:00–11:00 AM local-business website workflow, powered by local Ollama `qwen3:4b`.

## Goal

Find local businesses with no functioning official website, create a polished demo using free tools, and offer it for sale without upfront spend.

## Automatic 10 AM workflow

The Windows scheduled task runs `scripts/run-ollama-10am.ps1` every day at 10:00 AM IST. The local Qwen workflow is responsible for:

1. Searching worldwide for a verified local business and checking for a dedicated official website.
2. Generating an original demo website from verified facts only.
3. Testing and saving the website under `sites/<business>/`.
4. Creating the research note, email draft, WhatsApp draft, public screenshot links, and outreach record.
5. Updating `tracker/`, `work/`, and the Excel tracker.
6. Committing and pushing the complete run to this GitHub repository.
7. Sending outreach through the connected channel when available without asking for per-run permission, then recording the exact result for the owner.
8. If WhatsApp is unavailable, recording the reason and moving to another same-niche business with no official website instead of stopping the run.

Qwen does not invent business facts, prices, reviews, or services. Production deployment, payment collection, ownership transfer, and backend work happen only after owner approval and payment agreement. Routine website creation, GitHub/Excel updates, and outreach sending are authorized for the 10 AM workflow without a new permission request each day.

Codex is not the runtime for this workflow. The Codex heartbeat automation is paused; the local Windows Ollama task is the only scheduled runner.

## Operating rules

- Work only during the 10:00–11:00 AM IST window.
- Prefer free research, free development tools, GitHub, and free hosting tiers.
- Record evidence before marking a business as having no website.
- Contact-channel priority: record every reliable public phone, WhatsApp number, email, contact form, or social-message channel found, preserve its source URL, and use the available channel for outreach.
- Contact validation before build: verify that each discovered phone/WhatsApp number is correctly formatted and usable through the connected adapter, and verify that each email address is syntactically valid and accepted by the mail adapter before starting website creation.
- Template selection: choose a polished free template from the approved sources, especially ThemeWagon's free catalog, and record the template URL, repository, and license note before adapting it.
- Delivery sequence: deploy the finished demo to GitHub Pages, verify the live URL, capture clean current screenshots, then send the live link and screenshots by email and WhatsApp when available; record every result in the tracker.
- Outreach order: attempt public email, then WhatsApp, then phone call or SMS when the corresponding connected adapter is available; record each attempt and its exact result without claiming success unless visibly confirmed.
- Test demos on mobile and desktop.
- Ask the user to handle or approve payment collection.
- Never claim a message was sent unless the channel visibly reports sent/delivered.
- If a prospect has no usable WhatsApp channel, mark it clearly, ask the owner for a verified contact channel when required, and continue with another same-niche no-website prospect.
- Prospect discovery is global: if the local queue is empty, search other cities and countries for the same niche rather than reporting that there is no work.
- Before delivery, remove template/demo branding such as template names, years, “Free HTML5,” and original demo credits from the customer-facing footer; keep required legal attribution only in the project documentation/license record, and show `Developed by MultiMax`.
- Every outreach message must introduce Amala from MultiMax, explain that MultiMax creates affordable websites for local businesses, mention that the shop had no dedicated website, and say that the work can proceed at a low agreed budget.
- Standard introduction for every 10 AM outreach: “Hi, I’m Amala from MultiMax. MultiMax is a small web development company that creates affordable websites for local businesses. We found your shop and thought it looked great, but noticed it did not have a dedicated website, so we prepared a website concept for you. If you are interested, we can proceed and offer it at a low agreed budget. Tell me and I will send the website preview and full details.”
- Use public direct screenshot URLs when the GitHub repository is not accessible to the recipient.
- Deploy or transfer ownership only after acceptance and payment confirmation.

## Repository contents

- `docs/` — workflow notes and pricing guidance.
- `messages/` — outreach and follow-up templates.
- `tracker/` — spreadsheet/tracker export when the live workbook is available.
- `sites/` — demo websites for qualified prospects.
- `work/` — company-by-company work log, screenshots, README, and Excel tracker.
- `outreach/` — Qwen-generated channel drafts, links, attachments, and delivery status.

## Current example

`Mrs. Wilson's Cafe` has a Qwen-generated demo, two screenshots, a work log, an Excel tracker, and corrected WhatsApp outreach using public direct image URLs. The corrected message was delivered on 2026-10-20.

This repository is a review demo; outreach uses verified public contact channels and the 10 AM workflow reports the exact delivery result afterward. Production delivery and paid work still require owner acceptance.
