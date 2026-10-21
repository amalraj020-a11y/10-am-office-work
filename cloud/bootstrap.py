"""Register the EC2-only office agent without changing other agents or secrets."""
import json
import pathlib
import subprocess

HOME = pathlib.Path.home()
CONFIG = HOME / '.openclaw/openclaw.json'
WORKSPACE = HOME / '.openclaw/workspace-office'
MODEL = 'ollama/qwen3:0.6b'


def set_config(path, value):
    subprocess.run(['openclaw', 'config', 'set', path, json.dumps(value), '--strict-json'], check=True)


def main():
    config = json.loads(CONFIG.read_text())
    models = config['models']['providers']['ollama'].get('models', [])
    if not any(m['id'] == 'qwen3:0.6b' for m in models):
        models.append({
            'id': 'qwen3:0.6b', 'name': 'EC2 local Qwen 3 0.6B',
            'reasoning': False, 'input': ['text'],
            'cost': {'input': 0, 'output': 0, 'cacheRead': 0, 'cacheWrite': 0},
            'contextWindow': 16384, 'maxTokens': 1024,
            'compat': {'supportsTools': True, 'supportsUsageInStreaming': True},
            'params': {'num_ctx': 16384},
        })
        set_config('models.providers.ollama.models', models)
    allowed = config['agents']['defaults'].get('modelPolicy', {}).get('allow', [])
    if allowed and MODEL not in allowed:
        set_config('agents.defaults.modelPolicy.allow', allowed + [MODEL])
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    agent = config['agents'].get('entries', {}).get('amala-office', {})
    agent.update({
        'name': 'Amala 10 AM Office', 'workspace': str(WORKSPACE),
        'model': {'primary': MODEL, 'fallbacks': []},
        'tools': {'profile': 'full', 'allow': ['read', 'write', 'edit', 'exec', 'process', 'browser', 'web_fetch']},
    })
    set_config('agents.entries.amala-office', agent)
    target = WORKSPACE / 'AGENTS.md'
    if not target.exists():
        target.write_text(
            '# Amala office agent\n\n'
            'You are Amala, the MultiMax website assistant. Execute the assigned task using tools. '
            'Never invent a tool result, business fact, screenshot, deployment, or delivery. '
            'Use only the configured local Ollama Qwen model. No hosted model fallback. '
            'The repository is /home/ubuntu/amala-office-repo. Read cloud/RULEBOOK.md before daily work. '
            'Routine daily research, one qualified demo, GitHub Pages publishing and verified-channel outreach '
            'are authorized by Raj. No per-business permission question is needed. '
            'Do not contact anyone during a self-test. Never expose credentials or private conversations.\n'
        )
    print('Office agent registered; scheduler activation requires a passing self-test.')


if __name__ == '__main__':
    main()
