# EC2 office runtime setup

Status: installation is incomplete until the server preflight and scheduler update
have succeeded. Do not infer that the full workflow works from this repository.

Completed server checks: GitHub authentication as `amalraj020-a11y`, repository
access, enabled OpenClaw and Ollama services, user linger, and linked WhatsApp
account `amala`. The local Qwen 0.6B model has been registered in OpenClaw's catalog
and model allow-list. The browser/Excel dependency installation and a read-only
Qwen tool test were started; their final results still require server verification.

The existing 10 AM job is a check-in until `install_schedule.py` succeeds. Its
replacement uses existing Amala permissions, a local-model override without hosted
fallback, the full task in office-task.md, a 55-minute timeout, and its existing
owner-reporting destination. No new Codex automation is created.

Server installation:

```sh
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
git -C /home/ubuntu/amala-office-repo pull --ff-only
python3 /home/ubuntu/amala-office-repo/cloud/bootstrap.py
/home/ubuntu/.local/share/amala-office-venv/bin/python /home/ubuntu/amala-office-repo/cloud/install_schedule.py
```

The installer stops before changing the schedule if GitHub, browser dependencies
or Qwen's actual file-reading test fails. Even a passing smoke test does not prove
the entire research/build/deploy/outreach process. A full run must be checked by
its artifacts, deployment and message IDs before being reported as successful.

Utilities: artifacts.py captures desktop/mobile images from the business-specific
Pages URL and exports public run records to work/office-tracker.xlsx. The unified
Pages workflow replaces the three conflicting single-shop deployers and preserves
distinct websites/<slug>/ and sites/<slug>/ URLs. Historical templates and sites
remain intact; no old template is authorized for reuse.

Credentials stay on EC2, outside this repository. There is no configured email
adapter established by this setup, and WhatsApp registration lookup must still be
verified through the connected adapter before a phone-only prospect is built.
