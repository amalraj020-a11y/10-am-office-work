# EC2 office workflow

This is the authoritative specification for the EC2 10:00–11:00 Asia/Kolkata job.
OpenClaw owns scheduling, tools and sending. The office job uses existing agent `amala`
with an explicit `groq/qwen/qwen3.8-27b` override on the verified Groq Free plan
and no fallback. The user authorized this cloud-model change on 23 October. It does
not grant new tool permissions. Codex only installs and repairs
this runtime. This model must pass an actual tool-use test before activation;
an API connection alone is not proof that it can complete the job. Never upgrade
plans, add billing, or enable paid fallback. Honor rate limits and report incomplete
work honestly. Do not load local Ollama for this job on the memory-limited EC2 host.

1. Start at 10:00 Asia/Kolkata, use a process lock, and end within one hour. Work on
   at most one qualified business per day. Never rerun a completed prospect or send
   a message again just because a command timed out. Reconcile uncertain sends first.
2. Check Groq inference, GitHub authentication, browser, available storage,
   and the actual OpenClaw WhatsApp/email adapters. No Windows PC dependency.
3. Search worldwide for a new shop. Check public listings, search results, social
   profiles and linked official sites. Record source URLs and time checked. A missing
   search result alone does not prove that a website does not exist. Skip shops with
   a working official website or an uncertain identity.
4. Verify public contact information before building. Phone syntax is not WhatsApp
   registration. Require an actual connected-adapter lookup confirming WhatsApp
   availability. Email syntax and MX records do not prove mailbox delivery; record
   the confidence honestly. Use only configured email credentials, never guess them.
   If no channel can be verified, skip and research another same-niche shop.
5. Select a fresh free template from https://themewagon.com/theme-price/free/.
   Record the exact template page, source repository, pinned commit and license.
   Read data/used-templates.json and prior research notes; never reuse a previous
   prospect's template or the retired custom layout. Never silently substitute one.
6. Preserve legally required credits and license notices. If visible attribution
   cannot be removed for free, select a different template. Add `Developed by
   MultiMax`. Replace all demo identity, names, years, fake reviews, fake menu prices,
   contact information and placeholders with verified details or remove the section.
   Do not claim the unsolicited demo is the business's official website.
7. Build under `websites/<unique-business-slug>/`. Check all pages, mobile and desktop,
   links, images, forms and console errors. Do not present nonfunctional ordering,
   payments or database features as working. Use Qwen for copy and adaptation.
8. Deploy a demo to GitHub Pages in `amalraj020-a11y/10am-office-work`. Verify the
   business-specific live URL contains the right business name and MultiMax footer.
   Do not use a root URL pointing to another shop. Wait for the deployment to succeed.
9. Capture two different clean screenshots of the final live website. Open and
   inspect them, then verify their public URLs and source commit. No old screenshots.
10. Draft clear paragraphs with actual line breaks. Introduce Amala from MultiMax,
    explain that MultiMax builds affordable websites for local businesses, say that
    an independent concept was prepared, include the live preview, source link and
    both screenshots, and invite a reply to discuss a small agreed budget. Mention
    backend/database features only as optional later work. Do not invent credentials
    or promise an exact price. Do not assert website absence more strongly than evidence.
11. After all checks pass, send using OpenClaw's connected verified channel without
    asking Raj again. Send attachments, not only nonexistent screenshot links.
    Record provider message IDs and precise states: accepted/sent, delivered, bounced,
    failed or unknown. Accepted is not proof of delivered. Respect refusal/opt-out;
    no automatic repeated solicitation. No unsolicited calls or SMS in this workflow.
12. Update `work/<slug>/`, the website README, template-use registry and an Excel
    tracker with public business facts, research sources, license, model, code commit,
    live URL, screenshots, exact outreach text and outcome. Keep credentials, private
    chats, payment details and internal owner contact information out of the public repo.
13. Push the completed records and verify the push. Report to Raj through the existing
    OpenClaw owner channel after the run, including failures. Never claim completion
    without actual artifacts, a verified deployment and send evidence. Owner handles
    payment collection; production transfer and paid extras need a separate agreement.

The historical Windows script and check-in job are not implementations of this flow.
If a required capability fails, record the real blocker and report it; do not silently
fall back to Codex, another model provider, an old template, or a fabricated result.
