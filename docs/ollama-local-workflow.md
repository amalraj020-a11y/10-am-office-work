# Local Ollama workflow

The local runner uses `qwen3:4b` through the Ollama API at `127.0.0.1:11434`.

It generates a business-specific demo, research note, email/WhatsApp drafts, outreach queue, screenshots, work log, CSV tracker rows, and a GitHub commit. Before each run, add one verified local business to `data/prospects.json` with evidence that it has no official website.

The local Qwen runner does not guess contact details. Email and WhatsApp delivery require persistent authenticated adapters; when a connected browser/API adapter is available, the visible sent/delivered result must be written back to `outreach/`, `work/`, and the tracker. Without an adapter, it prepares the exact message and public screenshot links but does not pretend it sent them.

Codex is not part of the scheduled runtime. The Codex heartbeat is paused and the Windows Ollama task is the only 10 AM scheduler.

Run manually:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-ollama-10am.ps1
```
