"""Verify EC2 prerequisites and replace the existing check-in with the office job.

Run on EC2 with the office venv Python. Stops before changing the schedule when
the model cannot actually read a random fixture. It grants no agent permissions.
Passing this smoke test is not proof of full business-workflow completion.
"""
import json
import os
from pathlib import Path
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[1]
JOB = 'dc414724-bccf-4bc0-88b0-abbe624447f8'
MODEL = 'groq/qwen/qwen3.8-27b'
TEST_JOB = 'd8c5b65a-74b9-432d-a94a-d6e22d11f907'
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
    fixture = STATE / 'read-fixture.txt'
    expected = 'AMALA_' + uuid.uuid4().hex
    fixture.write_text(expected)
    run('openclaw', 'cron', 'edit', TEST_JOB,
        '--model', MODEL, '--fallbacks', '', '--tools', 'read',
        '--thinking', 'off', '--timeout-seconds', '180',
        '--message', f'Read {fixture} using the read tool. Reply with exactly the contents, nothing else. Do not guess. /no_think',
        '--disable')
    result = json.loads(run('openclaw', 'cron', 'run', TEST_JOB,
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
    run('openclaw', 'cron', 'edit', JOB,
        '--name', 'Amala 10 AM Website Office', '--cron', '0 10 * * *',
        '--tz', 'Asia/Kolkata', '--exact', '--agent', 'amala', '--session', 'isolated',
        '--model', MODEL, '--fallbacks', '', '--thinking', 'off', '--light-context',
        '--timeout-seconds', '3300', '--message', (ROOT / 'cloud/office-task.md').read_text(),
        '--enable')
    # Existing owner delivery account and destination are deliberately preserved.
    print('10 AM IST job installed with Groq Qwen; existing owner reporting preserved.')


if __name__ == '__main__':
    install()
