"""Verify EC2 prerequisites and replace the existing check-in with the office job.

Run on EC2 with the office venv Python. Stops before changing the schedule when
the model cannot actually read a random fixture. It grants no agent permissions.
Passing this smoke test is not proof of full business-workflow completion.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
JOB = 'dc414724-bccf-4bc0-88b0-abbe624447f8'
MODEL = 'groq/qwen/qwen3.8-27b'
STATE = Path.home() / '.local/share/amala-office'


def run(*args, timeout=60):
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        # Avoid dumping configuration or credential-bearing stderr to public logs.
        STATE.mkdir(parents=True, exist_ok=True)
        diagnostic = STATE / 'last-command-error.txt'
        diagnostic.write_text(result.stdout + '\n' + result.stderr)
        diagnostic.chmod(0o600)
        raise RuntimeError(f'{args[0]} {args[1]} failed with exit {result.returncode}; inspect locally')
    return result.stdout


def install():
    os.umask(0o077)
    STATE.mkdir(parents=True, exist_ok=True)
    if run('gh', 'api', 'user', '--jq', '.login').strip() != 'amalraj020-a11y':
        raise RuntimeError('Wrong GitHub account on EC2')
    from playwright.sync_api import sync_playwright
    import openpyxl  # noqa: F401 -- dependency preflight
    with sync_playwright() as p:
        executable = p.chromium.executable_path
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.set_content('<h1>Amala browser preflight</h1>')
            assert page.locator('h1').inner_text() == 'Amala browser preflight'
        finally:
            browser.close()
    fixture = ROOT / '.openclaw/tmp/read-fixture.txt'
    fixture.parent.mkdir(parents=True, exist_ok=True)
    expected = 'AMALA_' + uuid.uuid4().hex
    fixture.write_text(expected)
    # Previous one-shot tests were deleted after success. Create a fresh disabled
    # fixture job instead of relying on a stale hard-coded automation ID.
    created = json.loads(run('openclaw', 'cron', 'add',
        '--name', 'Amala read preflight ' + uuid.uuid4().hex[:8],
        '--at', '24h', '--disabled', '--keep-after-run', '--json',
        '--agent', 'amala-office', '--session', 'isolated', '--no-deliver',
        '--model', MODEL, '--fallbacks', '', '--tools', 'read',
        '--thinking', 'off', '--timeout-seconds', '180',
        '--message', f'Read {fixture} using the read tool. Reply with exactly the contents, nothing else. Do not guess. /no_think'))
    test_job = created.get('job', created).get('id')
    if not test_job:
        raise RuntimeError('Preflight job creation returned no ID')
    result = json.loads(run('openclaw', 'cron', 'run', test_job,
                            '--wait', '--wait-timeout', '4m', '--json', timeout=270))
    outcome = result.get('run', {})
    passed = (outcome.get('status') == 'ok'
              and expected in outcome.get('summary', '')
              and outcome.get('provider') == 'groq'
              and outcome.get('model') == 'qwen/qwen3.8-27b')
    (STATE / 'preflight.json').write_text(json.dumps({
        'model': MODEL, 'read_tool_test_passed': passed, 'browser': executable,
        'github_account': 'amalraj020-a11y', 'full_workflow_tested': False,
    }, indent=2))
    if not passed:
        raise RuntimeError('Groq Qwen failed the verified tool-use test; schedule not changed')
    backup = run('openclaw', 'cron', 'get', JOB)
    (STATE / 'previous-10am-job.json').write_text(backup)
    run('openclaw', 'config', 'set', 'browser.executablePath', json.dumps(executable), '--strict-json')
    run('openclaw', 'config', 'set', 'browser.headless', 'true', '--strict-json')
    run('openclaw', 'cron', 'edit', test_job, '--tools', '', '--light-context',
        '--timeout-seconds', '180', '--no-deliver', '--disable')
    probe_script = STATE / 'initial-execution-probe.js'
    probe_script.write_text("const r = await exec({command:'printf AMALA_STEP_OK',timeoutSeconds:30}); json({notify:JSON.stringify(r)});\n")
    execution = json.loads(run('openclaw', 'cron', 'add',
        '--name', 'Amala bounded execution ' + uuid.uuid4().hex[:8],
        '--at', '24h', '--disabled', '--keep-after-run', '--json',
        '--agent', 'amala-office', '--session', 'isolated', '--no-deliver',
        '--tools', 'exec', '--script', str(probe_script),
        '--script-tool-budget', '1', '--script-timeout-seconds', '120'))
    execution_job = execution.get('job', execution).get('id')
    if not execution_job:
        raise RuntimeError('Execution job creation returned no ID')
    config_path = STATE / 'step-runner.json'
    existing = json.loads(config_path.read_text()) if config_path.exists() else {}
    job_record = json.loads(backup)
    owner = existing.get('owner') or job_record.get('job', job_record).get('delivery', {}).get('to')
    if not owner:
        raise RuntimeError('Existing owner reporting destination could not be resolved')
    config_path.write_text(json.dumps({'step_job': execution_job, 'decision_job': test_job, 'owner': owner}))
    config_path.chmod(0o600)
    run(sys.executable, str(ROOT / 'cloud/step_runner.py'), '--test', '--max-steps', '1', timeout=310)
    run(sys.executable, str(ROOT / 'cloud/install_step_schedule.py'), timeout=120)
    print('Bounded 10 AM IST runner installed; owner reporting preserved.')


if __name__ == '__main__':
    install()
