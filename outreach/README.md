# Outreach queue

Each JSON file contains Qwen-generated email and WhatsApp content. `queued_for_auto_send` means OpenClaw is authorized to send through the connected adapter without asking for permission before sending; the owner receives the exact result afterward. Codex must never send, orchestrate, or act as a fallback. If OpenClaw is unavailable, record `openclaw_not_connected` and stop. If no reliable phone number or email is found after searching public listings, record `owner_contact_required` and ask the owner in WhatsApp for a verified contact channel.
