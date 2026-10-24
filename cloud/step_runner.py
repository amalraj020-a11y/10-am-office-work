"""Bounded OpenClaw/Qwen office steps; no direct model API or credential reads.

The OpenClaw daily command calls --launch and releases its scheduler slot.
This worker calls the disabled step job through the authenticated local gateway.
Each step gets a fresh isolated conversation and a compact persistent handoff.
"""
import argparse
from datetime import datetime
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
STATE = Path.home() / '.local/share/amala-office'
MODEL = 'qwen/qwen3.8-27b'


def cli(*args, timeout=240):
    proc = subprocess.run(['openclaw', *args], capture_output=True, text=True,
                          timeout=timeout, cwd=ROOT)
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(proc.stderr[-1200:] or 'No structured CLI result')
    if proc.returncode and not result.get('completed'):
        error = result.get('error', {})
        raise RuntimeError(error.get('message', 'CLI failed') if isinstance(error, dict) else str(error))
    return result


def validate_step(result):
    run = result.get('run', {})
    if not result.get('completed'):
        raise RuntimeError('Step completion is unknown; do not redispatch it.')
    if run.get('provider') != 'groq' or run.get('model') != MODEL:
        raise RuntimeError('Unexpected model route; stopped.')
    if run.get('status') != 'ok':
        raise RuntimeError(run.get('error', 'Step failed; inspect recorded effects.'))
    return run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--launch', action='store_true')
    parser.add_argument('--max-steps', type=int, default=30)
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()
    os.umask(0o077)
    STATE.mkdir(parents=True, exist_ok=True)
    if args.launch:
        # The child must outlive the short scheduler command and the user's PC.
        with (STATE / 'worker.log').open('a') as log:
            subprocess.Popen([sys.executable, str(Path(__file__).resolve())],
                             cwd=ROOT, stdout=log, stderr=log,
                             stdin=subprocess.DEVNULL, start_new_session=True)
        print('EC2 office worker started. This is not a completion report.')
        return
    with (STATE / 'worker.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('Existing office worker owns this run; no duplicate started.')
            return
        config = json.loads((STATE / 'step-runner.json').read_text())
        day = datetime.now(ZoneInfo('Asia/Kolkata')).date().isoformat()
        run_dir = STATE / 'runs' / (day + ('-test-' + str(int(time.time())) if args.test else ''))
        run_dir.mkdir(parents=True, exist_ok=True)
        # A retry may have already sent something. Never silently start over.
        if (run_dir / 'started.json').exists():
            print('Today already attempted. Reconcile recorded outcomes before retrying.')
            return
        (run_dir / 'started.json').write_text(json.dumps({'started': time.time()}))
        deadline = time.monotonic() + 55 * 60
        handoff = ('Inspect available browser and WhatsApp CLI capabilities and previous '
                   'business/template records. Select a NEW prospect only after that. '
                   'First perform one small prerequisite inspection; no outreach yet.')
        rules = (ROOT / 'cloud/runtime-rules.md').read_text()
        instructions = (ROOT / 'cloud/office-step.md').read_text()
        total_tokens = 0
        outcome = 'incomplete'
        reason = 'Time or step budget reached; saved work requires continuation.'
        try:
            for index in range(args.max_steps):
                if time.monotonic() + 240 > deadline or total_tokens >= 160000:
                    break
                if args.test:
                    prompt = instructions + '\nRULES:\n' + rules + '\nTEST OVERRIDE:\n' + ('Use exec once to run: printf AMALA_STEP_OK. Report the actual '
                              'output and stop. Do not send messages or change any files.')
                else:
                    prompt = instructions + '\nRULES:\n' + rules + '\nLAST HANDOFF:\n' + handoff
                cli('cron', 'edit', config['step_job'], '--message', prompt, '--disable')
                # Persist intent before dispatch. A timeout never triggers a resend.
                (run_dir / f'{index:02d}-intent.json').write_text(json.dumps({'time': time.time()}))
                result = cli('cron', 'run', config['step_job'], '--wait',
                             '--wait-timeout', '4m', '--json', timeout=260)
                (run_dir / f'{index:02d}-result.json').write_text(json.dumps(result, indent=2))
                run = validate_step(result)
                total_tokens += run.get('usage', {}).get('total_tokens', 0)
                handoff = run.get('summary', '')[:2200]
                (run_dir / 'handoff.txt').write_text(handoff)
                if args.test:
                    if 'AMALA_STEP_OK' not in handoff:
                        raise RuntimeError('Probe output did not match')
                    outcome, reason = 'probe_passed', 'Fresh-session OpenClaw tool probe passed.'
                    break
                # A model summary alone is never accepted as verified completion.
                if 'COMPLETE' in handoff or 'BLOCKED' in handoff:
                    reason = 'Agent returned a terminal handoff; review its artifact/send evidence.\n' + handoff
                    break
                # Free quota is per minute; avoid immediately starting another step.
                time.sleep(65)
        except Exception as exc:
            reason = str(exc)[:2000]
        report = {'status': outcome, 'reason': reason, 'tokens': total_tokens,
                  'model': 'groq/' + MODEL, 'finished': time.time()}
        (run_dir / 'result.json').write_text(json.dumps(report, indent=2))
        print(json.dumps(report), flush=True)
        if args.test and outcome != 'probe_passed':
            raise SystemExit(1)
        if not args.test:
            message = ('Amala 10 AM EC2 run: ' + outcome + '.\n' + reason +
                       '\nNo completion is claimed without deployment and message evidence.')
            try:
                sent = cli('message', 'send', '--channel', 'whatsapp', '--account', 'amala',
                           '--target', config['owner'], '--message', message, '--json')
            except Exception as exc:
                sent = {'status': 'unknown', 'error': str(exc)[:1000],
                        'retry': 'Do not resend until delivery has been reconciled.'}
            (run_dir / 'owner-report.json').write_text(json.dumps(sent, indent=2))


if __name__ == '__main__':
    main()
