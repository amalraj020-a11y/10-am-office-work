# Outreach queue

Each JSON file contains Qwen-generated email and WhatsApp content. `pending_user_send` means the prefilled WhatsApp link is ready for review; the local Ollama process does not silently send external messages. If no reliable phone number or email is found after searching public listings, record `owner_contact_required` and ask the owner in WhatsApp for a verified contact channel.
