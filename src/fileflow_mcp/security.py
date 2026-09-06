import json
import threading
import time
from collections import deque

from watch_config import FILEFLOW_HOME

__all__ = ['ToolPolicy', 'create_policy']

WINDOW_SECONDS = 60
AUDIT_PATH = FILEFLOW_HOME / "mcp_audit.jsonl"


def create_policy(rate_limit=60, log_audit=True):
    return ToolPolicy(rate_limit=rate_limit, log_audit=log_audit)


class ToolPolicy:
    def __init__(self, rate_limit=60, log_audit=True):
        self.rate_limit = rate_limit
        self.log_audit = log_audit
        self.blocked_tools = set()
        self._lock = threading.Lock()
        self._timestamps = deque()
        self.audit_path = AUDIT_PATH

    def block_tool(self, name):
        with self._lock:
            self.blocked_tools.add(name)

    def check(self, name):
        with self._lock:
            if name in self.blocked_tools:
                raise PermissionError(f"Tool '{name}' esta bloqueado pelo policy do FileFlow.")
            now = time.time()
            while self._timestamps and now - self._timestamps[0] > WINDOW_SECONDS:
                self._timestamps.popleft()
            if self.rate_limit and len(self._timestamps) >= self.rate_limit:
                raise PermissionError(
                    f"Rate limit atingido ({self.rate_limit}/min). Tente novamente em instantes."
                )
            self._timestamps.append(now)

    def audit(self, name, args=None, result=None, error=None):
        if not self.log_audit:
            return
        entry = {
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'tool': name,
            'args': args or {},
            'result': result,
            'error': error,
        }
        try:
            self.audit_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.audit_path, 'a') as f:
                f.write(json.dumps(entry, default=str) + "\n")
        except OSError:
            pass