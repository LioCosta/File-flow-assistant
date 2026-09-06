import functools
import json
import os
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent
_PKG = Path(__file__).resolve().parent
for _p in (_SRC, _PKG):
    _s = str(_p)
    if _s not in sys.path:
        sys.path.insert(0, _s)

from mcp.server.fastmcp import FastMCP

from config import (
    WATCH_DIRECTORIES, TEMP_BASE_DIR, TEMP_CATEGORIES,
    KEYWORD_PATTERNS, IGNORE_PATTERNS, TRIGGER_INACTIVITY_HOURS,
    WATCH_RECURSIVELY, TRASH_DIR, METADATA_FILE, FILEFLOW_HOME,
)
from duplicate import DuplicateDetector
from fileflow_mcp.security import create_policy
from organizer import FileOrganizer
from rules import load_rules, add_rule, remove_rule
from scanner import VirusScanner
from services import (
    get_status_data, db_info, db_reset,
    trash_list, trash_recover, trash_clean,
)
from trash import soft_delete
from watch_config import load_dirs, add_dir, remove_dir

__all__ = ['create_fileflow_mcp', 'main']


class _ServerLogger:
    def __init__(self, log_file):
        self.log_file = log_file
        self._log_path = Path(log_file)
        try:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            self._log_path = None

    def _write(self, text):
        print(text, file=sys.stderr)
        if self._log_path is not None:
            try:
                with open(self._log_path, 'a', encoding='utf-8') as f:
                    f.write(text + '\n')
            except OSError:
                pass

    def info(self, message):
        self._write(f"[FileFlow] INFO {message}")

    def debug(self, message):
        self._write(f"[FileFlow] DEBUG {message}")

    def warning(self, message):
        self._write(f"[FileFlow] WARNING {message}")

    def error(self, message):
        self._write(f"[FileFlow] ERROR {message}")


def _logger():
    return _ServerLogger(log_file='logs/fileflow_mcp.log')


def _organizer():
    return FileOrganizer(
        logger=_logger(),
        watch_dirs=WATCH_DIRECTORIES,
        temp_base=TEMP_BASE_DIR,
        categories=TEMP_CATEGORIES,
        patterns=KEYWORD_PATTERNS,
        ignore_patterns=IGNORE_PATTERNS,
        inactivity_hours=TRIGGER_INACTIVITY_HOURS,
    )


def _daemon_info():
    pid_file = FILEFLOW_HOME / "fileflow.pid"
    if not pid_file.exists():
        return {'running': False, 'pid': None}
    try:
        pid = int(pid_file.read_text().strip())
        os.kill(pid, 0)
        return {'running': True, 'pid': pid}
    except (ProcessLookupError, ValueError, OSError):
        return {'running': False, 'pid': None}


def _secure(policy, name):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if policy is not None:
                policy.check(name)
            try:
                result = fn(*args, **kwargs)
                if policy is not None:
                    policy.audit(name, kwargs, result)
                return result
            except Exception as exc:
                if policy is not None:
                    policy.audit(name, kwargs, None, str(exc))
                raise
        return wrapper
    return decorator


def create_fileflow_mcp(security=None):
    mcp = FastMCP("fileflow")
    policy = security

    @mcp.tool()
    @_secure(policy, "fileflow_status")
    def fileflow_status() -> dict:
        data = get_status_data()
        trash_count = 0
        if METADATA_FILE.exists():
            try:
                with open(METADATA_FILE, 'r') as f:
                    metadata = json.load(f)
                trash_count = len(metadata) if isinstance(metadata, dict) else 0
            except (json.JSONDecodeError, ValueError):
                pass
        data['trash_count'] = trash_count
        data['daemon'] = _daemon_info()
        return data

    @mcp.tool()
    @_secure(policy, "fileflow_scan_duplicates")
    def fileflow_scan_duplicates(limit: int = 50) -> dict:
        detector = DuplicateDetector(_logger(), WATCH_DIRECTORIES)
        detector._scan_existing_files()
        duplicates = detector.generate_report()
        return {
            'total': len(duplicates),
            'duplicates': [d for d in duplicates[:max(0, limit)]],
        }

    @mcp.tool()
    @_secure(policy, "fileflow_organize_preview")
    def fileflow_organize_preview() -> dict:
        files = _organizer().preview(recursive=WATCH_RECURSIVELY)
        return {
            'total': len(files),
            'files': [
                {
                    'source': str(f['source']),
                    'dest': str(f['dest']),
                    'category': f['category'],
                    'size': f['size'],
                }
                for f in files
            ],
        }

    @mcp.tool()
    @_secure(policy, "fileflow_organize_run")
    def fileflow_organize_run(confirm: bool = False) -> dict:
        organizer = _organizer()
        files = organizer.preview(recursive=WATCH_RECURSIVELY)
        if not confirm:
            return {
                'moved': 0,
                'total': len(files),
                'confirm_required': True,
                'message': 'Passe confirm=True para mover os arquivos para as categorias.',
            }
        moved = sum(1 for f in files if organizer.organize_file(f['source']))
        return {'moved': moved, 'total': len(files), 'confirm_required': False}

    @mcp.tool()
    @_secure(policy, "fileflow_trash_list")
    def fileflow_trash_list() -> dict:
        items = trash_list() or []
        return {'total': len(items), 'items': items}

    @mcp.tool()
    @_secure(policy, "fileflow_trash_recover")
    def fileflow_trash_recover(identifier: str) -> dict:
        dest, error = trash_recover(identifier)
        if error:
            return {'recovered': False, 'destination': None, 'error': error}
        return {'recovered': True, 'destination': str(dest), 'error': None}

    @mcp.tool()
    @_secure(policy, "fileflow_trash_clean")
    def fileflow_trash_clean() -> dict:
        return {'removed': trash_clean()}

    @mcp.tool()
    @_secure(policy, "fileflow_watch_list")
    def fileflow_watch_list() -> dict:
        dirs = load_dirs()
        return {
            'total': len(dirs),
            'directories': [{'path': d, 'exists': os.path.isdir(d)} for d in dirs],
        }

    @mcp.tool()
    @_secure(policy, "fileflow_watch_add")
    def fileflow_watch_add(path: str) -> dict:
        added, expanded, error = add_dir(path)
        return {'added': added, 'path': expanded, 'error': error}

    @mcp.tool()
    @_secure(policy, "fileflow_watch_remove")
    def fileflow_watch_remove(path: str) -> dict:
        removed, expanded, error = remove_dir(path)
        return {'removed': removed, 'path': expanded, 'error': error}

    @mcp.tool()
    @_secure(policy, "fileflow_rules_list")
    def fileflow_rules_list() -> dict:
        rules = load_rules()
        return {
            'total': len(rules),
            'rules': [
                {'name': r.name, 'conditions': r.conditions, 'action': r.action}
                for r in rules
            ],
        }

    @mcp.tool()
    @_secure(policy, "fileflow_rule_add")
    def fileflow_rule_add(
        name: str,
        dest: str,
        extension: str = None,
        keyword: str = None,
    ) -> dict:
        conditions = {}
        if extension:
            conditions['extension'] = extension.lower()
        if keyword:
            conditions['keyword'] = keyword
        if not conditions:
            return {'added': False, 'error': 'Informe extension ou keyword.'}
        add_rule(name, conditions, {'type': 'move', 'dest': dest})
        return {'added': True, 'name': name, 'conditions': conditions}

    @mcp.tool()
    @_secure(policy, "fileflow_rule_remove")
    def fileflow_rule_remove(name: str) -> dict:
        remove_rule(name)
        return {'removed': True, 'name': name}

    @mcp.tool()
    @_secure(policy, "fileflow_db_info")
    def fileflow_db_info() -> dict:
        return db_info()

    @mcp.tool()
    @_secure(policy, "fileflow_db_reset")
    def fileflow_db_reset(confirm: bool = False) -> dict:
        if not confirm:
            return {
                'reset': False,
                'confirm_required': True,
                'message': 'Passe confirm=True para apagar o banco de dados.',
            }
        db_reset()
        return {'reset': True}

    @mcp.tool()
    @_secure(policy, "fileflow_malware_scan_file")
    def fileflow_malware_scan_file(file: str) -> dict:
        scanner = VirusScanner()
        if not scanner.is_available():
            return {
                'status': 'unavailable',
                'message': 'Nenhum antivirus encontrado (ClamAV ou Windows Defender).',
            }
        result = scanner.scan_file(file)
        if isinstance(result, dict):
            return result
        return {'status': 'error', 'message': str(result)}

    @mcp.tool()
    @_secure(policy, "fileflow_malware_scan_dir")
    def fileflow_malware_scan_dir(dir_path: str) -> dict:
        scanner = VirusScanner()
        if not scanner.is_available():
            return {
                'status': 'unavailable',
                'message': 'Nenhum antivirus encontrado (ClamAV ou Windows Defender).',
            }
        results = scanner.scan_directory(dir_path)
        infected = [r for r in results if r.get('status') == 'infected']
        clean = sum(1 for r in results if r.get('status') == 'clean')
        errors = sum(1 for r in results if r.get('status') == 'error')
        return {
            'total': len(results),
            'clean': clean,
            'infected': len(infected),
            'errors': errors,
            'infected_files': infected,
        }

    @mcp.tool()
    @_secure(policy, "fileflow_delete")
    def fileflow_delete(path: str) -> dict:
        if not os.path.isfile(path):
            return {'deleted': False, 'error': f'Arquivo nao encontrado: {path}'}
        soft_delete(path)
        return {'deleted': True, 'path': path, 'trash': str(TRASH_DIR)}

    @mcp.tool()
    @_secure(policy, "fileflow_daemon_status")
    def fileflow_daemon_status() -> dict:
        return _daemon_info()

    return mcp


def main():
    from fileflow_mcp.mcp_config import load_mcp_config

    config = load_mcp_config()
    policy = create_policy(
        rate_limit=config.get('rate_limit', 60),
        log_audit=config.get('log_audit', True),
    )
    for name in config.get('blocked_tools', []):
        policy.block_tool(name)

    mcp = create_fileflow_mcp(security=policy)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()