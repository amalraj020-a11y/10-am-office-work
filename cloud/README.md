# EC2 office runtime setup

Status on 24 October 2026: the daily 10 AM Asia/Kolkata office schedule is installed
and enabled on EC2 using Groq Qwen. The full-rulebook, fresh-session tool probe
passed. The daily command now starts amala-office.service, which runs small Qwen
steps through the existing OpenClaw gateway. End-to-end outreach is not yet verified.

Completed server checks: GitHub authentication as `amalraj020-a11y`, repository
access, enabled OpenClaw and Ollama services, user linger, and linked WhatsApp
account `amala`. Browser and Excel dependencies are installed and the browser
preflight passed. The existing EC2 Groq API credential works. Groq's account UI
confirmed the Free plan. The office model is `groq/qwen/qwen3.8-27b`, with no
fallbacks. No API key is stored in this repository.

The first agent test was killed by Ollama's 850 MiB service memory cap. On
23 October a trial with MemoryHigh 950 MiB and MemoryMax 1200 MiB caused the
OpenClaw gateway to be killed by the OOM killer during testing. The previous
650 MiB/850 MiB Ollama limits were restored to protect the existing services.
The 2 GiB instance has not demonstrated capacity for this workflow. No instance
resize was performed. The user subsequently approved Groq's Free plan instead.

The previous 10 AM check-in is replaced by the office job. The original long
conversation overflowed Groq's free request limit. step_runner.py now gives each
small action a fresh isolated OpenClaw session, the rulebook and a saved handoff.
It uses existing Amala permissions, explicit Groq Qwen with no fallback, a process
lock, a 55-minute deadline and a bounded token budget. The systemd service survives
the Windows PC shutting down. OpenClaw starts it daily at 10 AM Asia/Kolkata.
Private run state stays under ~/.local/share/amala-office/runs. Unknown results
are not automatically replayed. The worker sends the actual outcome to the existing
owner destination. A successful launcher alone does not mean business work finished.

Server installation:

```sh
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
git -C /home/ubuntu/amala-office-repo pull --ff-only
python3 /home/ubuntu/amala-office-repo/cloud/groq_setup.py
/home/ubuntu/.local/share/amala-office-venv/bin/python /home/ubuntu/amala-office-repo/cloud/install_schedule.py
```

The installer stops before changing the schedule if GitHub, browser dependencies
or Qwen's tool probes fail. Even a passing smoke test does not prove
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
