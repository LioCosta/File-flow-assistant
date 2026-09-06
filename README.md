# FileFlow

> [Portugues](README.pt.md) | English🇺🇸

Intelligent file organizer that monitors folders, detects duplicates, and keeps your files safe.

## Features

- **Real-time monitoring** — watches folders and reacts to file changes
- **Duplicate detection** — SHA-256 hashing, generates reports (never deletes automatically)
- **Soft delete** — deleted files go to hidden trash (`~/.fileflow_trash`), recoverable for 30 days
- **Auto organization** — moves inactive files by type/extension/keyword
- **Virus scanning** — integrates with ClamAV (Linux) or Windows Defender
- **Daemon mode** — runs in background, persists after terminal close
- **MCP server** — AI integration via Model Context Protocol (19 tools)

## Install

```bash
git clone https://github.com/LioExp/File-flow-assistant.git
cd File-flow-assistant
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# Dashboard
ff

# Start monitoring
ff start

# Start as daemon (background)
ff start --daemon

# Scan for duplicates
ff scan

# Organize files
ff organize

# View trash
ff trash
```

The `ff` alias runs from anywhere. You can also call `fileflow` or `python src/main.py` directly.

## Commands

| Command | Description |
|---------|-------------|
| `ff` | Show dashboard |
| `ff version` | Show FileFlow version |
| `ff start` | Start monitoring |
| `ff start --daemon` | Start in background (add `--mcp` for MCP) |
| `ff stop` | Stop daemon |
| `ff restart` | Restart daemon |
| `ff scan` | Scan for duplicates |
| `ff report` | Generate duplicate report |
| `ff organize` | Organize inactive files |
| `ff trash` | View trash |
| `ff recover <file>` | Recover from trash |
| `ff clean` | Remove expired trash files |
| `ff status` | Show dashboard |
| `ff db info` / `db reset` | Database info / reset |
| `ff watch` / `watch-add` / `watch-remove` | Manage monitored dirs |
| `ff rules` / `rules-add` / `rules-remove` | Manage organization rules |
| `ff scanfile <file>` | Scan file for malware |
| `ff scandir <dir>` | Scan directory for malware |
| `ff scanwatch` | Scan all monitored dirs |
| `ff daemon-status` | Check daemon status |
| `ff service-install` | Install systemd service |

## MCP Integration

FileFlow exposes an MCP server with 19 tools (status, duplicates, organize, trash, watch dirs, rules, database, malware scan, soft delete, daemon).

```bash
# Run the MCP server standalone (stdio)
./venv/bin/python src/fileflow_mcp/server.py

# Run via CLI
ff mcp-tools          # list available tools
ff mcp-enable         # enable MCP
ff mcp-disable        # disable MCP
ff start --mcp        # start monitoring with MCP
```

Available tools: `fileflow_status`, `fileflow_scan_duplicates`, `fileflow_organize_preview`, `fileflow_organize_run`, `fileflow_trash_list`, `fileflow_trash_recover`, `fileflow_trash_clean`, `fileflow_watch_list`, `fileflow_watch_add`, `fileflow_watch_remove`, `fileflow_rules_list`, `fileflow_rule_add`, `fileflow_rule_remove`, `fileflow_db_info`, `fileflow_db_reset`, `fileflow_malware_scan_file`, `fileflow_malware_scan_dir`, `fileflow_delete`, `fileflow_daemon_status`.

Destructive tools (`fileflow_organize_run`, `fileflow_db_reset`) require explicit `confirm=True`.

### Configuration

MCP settings live in `~/.fileflow/mcp_config.json` (rate limit, blocked tools, audit log).

```bash
ff mcp          # show MCP configuration
ff mcp-audit    # view audit log
```

## Tech Stack

- Python 3.10+
- watchdog (file monitoring)
- SQLite (index storage)
- Rich (terminal UI)
- MCP SDK (AI integration, FastMCP)
