import json

from watch_config import FILEFLOW_HOME

__all__ = ['MCP_CONFIG_PATH', 'DEFAULT_CONFIG', 'load_mcp_config', 'save_mcp_config']

MCP_CONFIG_PATH = FILEFLOW_HOME / "mcp_config.json"

DEFAULT_CONFIG = {
    'enabled': False,
    'transport': 'stdio',
    'port': 8080,
    'rate_limit': 60,
    'log_audit': True,
    'blocked_tools': [],
}


def load_mcp_config():
    config = dict(DEFAULT_CONFIG)
    if MCP_CONFIG_PATH.exists():
        try:
            with open(MCP_CONFIG_PATH, 'r') as f:
                data = json.load(f)
            if isinstance(data, dict):
                config.update({k: v for k, v in data.items() if k in DEFAULT_CONFIG})
        except (json.JSONDecodeError, ValueError):
            pass
    return config


def save_mcp_config(config):
    MCP_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {k: config.get(k, DEFAULT_CONFIG[k]) for k in DEFAULT_CONFIG}
    with open(MCP_CONFIG_PATH, 'w') as f:
        json.dump(data, f, indent=2)