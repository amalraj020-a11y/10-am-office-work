"""Install the tested bounded runner without changing other OpenClaw jobs."""
import json
from pathlib import Path
import subprocess

from install_schedule import JOB, ROOT, STATE, run


def main():
    config = json.loads((STATE / 'step-runner.json').read_text())
    passed = []
    for path in (STATE / 'runs').glob('*-test-*/result.json'):
        report = json.loads(path.read_text())
        if report.get('status') == 'probe_passed' and report.get('model') == 'groq/qwen/qwen3.8-27b':
            passed.append(path)
    if not passed:
        raise RuntimeError('Full-rulebook step probe must pass before installation')
    step = json.loads(run('openclaw', 'cron', 'get', config['step_job'], '--json'))
    payload = step.get('job', step)['payload']
    if (payload.get('model') != 'groq/qwen/qwen3.8-27b'
            or payload.get('fallbacks') != [] or payload.get('toolsAllow') != ['exec']):
        raise RuntimeError('Step job must use only the authorized Qwen route and exec tool')
    backup = STATE / 'before-step-schedule.json'
    if not backup.exists():
        backup.write_text(run('openclaw', 'cron', 'get', JOB, '--json'))
        backup.chmod(0o600)
    units = Path.home() / '.config/systemd/user'
    units.mkdir(parents=True, exist_ok=True)
    (units / 'amala-office.service').write_text(f'''[Unit]
Description=Amala bounded daily website office
After=openclaw-gateway.service
Requires=openclaw-gateway.service

[Service]
Type=exec
WorkingDirectory={ROOT}
Environment=PATH=/home/ubuntu/.npm-global/bin:/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/bin/python3 {ROOT}/cloud/step_runner.py
RuntimeMaxSec=58min
KillMode=control-group
Restart=no
UMask=0077
''')
    subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
    run('openclaw', 'cron', 'edit', JOB,
        '--name', 'Amala 10 AM Website Office', '--cron', '0 10 * * *',
        '--tz', 'Asia/Kolkata', '--exact', '--agent', 'amala', '--session', 'isolated',
        '--command-argv', json.dumps(['systemctl', '--user', 'start', '--no-block', 'amala-office.service']),
        '--timeout-seconds', '60', '--no-deliver', '--enable')
    print('10 AM IST now starts the bounded EC2 service; the worker reports its actual outcome.')


if __name__ == '__main__':
    main()
