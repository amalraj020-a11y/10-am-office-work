# Local Ollama workflow

The local runner uses `qwen3:4b` through the Ollama API at `127.0.0.1:11434`.

It generates a business-specific demo, research note, email/WhatsApp drafts, CSV tracker rows, and a GitHub commit. Before each run, replace the placeholder record in `data/prospects.json` with one verified local business and evidence that it has no official website.

The runner does not guess contact details and does not send external messages by itself. WhatsApp and email require persistent authenticated adapters. The current output is safe for review before outreach.

Run manually:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-ollama-10am.ps1
```
