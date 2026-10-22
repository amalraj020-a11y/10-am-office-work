"""Register the local model without changing any agent's tool permissions."""
import json
import pathlib
import subprocess

HOME = pathlib.Path.home()
CONFIG = HOME / '.openclaw/openclaw.json'
MODEL = 'ollama/qwen3:0.6b'


def set_config(path, value):
    subprocess.run(['openclaw', 'config', 'set', path, json.dumps(value), '--strict-json'], check=True)


def main():
    config = json.loads(CONFIG.read_text())
    plugins = config.get('plugins', {}).get('allow', [])
    if plugins and 'ollama' not in plugins:
        set_config('plugins.allow', plugins + ['ollama'])
    set_config('plugins.entries.ollama.enabled', True)
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
    print('Local model registered. Existing Amala tool permissions are unchanged.')


if __name__ == '__main__':
    main()
