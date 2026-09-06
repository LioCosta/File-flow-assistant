# FileFlow

> Portugues | [English](README.md)

Organizador inteligente de ficheiros que monitoriza pastas, deteta duplicados e mantém os teus ficheiros seguros.

## Funcionalidades

- **Monitoramento em tempo real** — observa pastas e reage a alterações
- **Deteção de duplicados** — hash SHA-256, gera relatórios (nunca apaga automaticamente)
- **Soft delete** — ficheiros apagados vão para lixeira oculta (`~/.fileflow_trash`), recuperáveis por 30 dias
- **Organização automática** — move ficheiros inativos por tipo/extensão/palavra-chave
- **Scanner de vírus** — integra com ClamAV (Linux) ou Windows Defender
- **Modo daemon** — corre em segundo plano, persiste após fechar terminal
- **Servidor MCP** — integração com IA via Model Context Protocol (19 tools)

## Instalação

```bash
git clone https://github.com/LioExp/File-flow-assistant.git
cd File-flow-assistant
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Uso

```bash
# Dashboard
ff

# Iniciar monitoramento
ff start

# Iniciar como daemon (segundo plano)
ff start --daemon

# Escanear duplicados
ff scan

# Organizar ficheiros
ff organize

# Ver lixeira
ff trash
```

O atalho `ff` funciona de qualquer diretório. Podes também chamar `fileflow` ou `python src/main.py` diretamente.

## Comandos

| Comando | Descrição |
|---------|-----------|
| `ff` | Mostrar dashboard |
| `ff version` | Mostrar versão do FileFlow |
| `ff start` | Iniciar monitoramento |
| `ff start --daemon` | Iniciar em segundo plano (usar `--mcp` para MCP) |
| `ff stop` | Parar daemon |
| `ff restart` | Reiniciar daemon |
| `ff scan` | Escanear duplicados |
| `ff report` | Gerar relatório de duplicados |
| `ff organize` | Organizar ficheiros inativos |
| `ff trash` | Ver lixeira |
| `ff recover <ficheiro>` | Recuperar da lixeira |
| `ff clean` | Remover ficheiros expirados da lixeira |
| `ff status` | Mostrar dashboard |
| `ff db info` / `db reset` | Info / reset da base de dados |
| `ff watch` / `watch-add` / `watch-remove` | Gerir pastas monitorizadas |
| `ff rules` / `rules-add` / `rules-remove` | Gerir regras de organização |
| `ff scanfile <ficheiro>` | Escanear ficheiro para vírus |
| `ff scandir <pasta>` | Escanear pasta para vírus |
| `ff scanwatch` | Escanear todas as pastas monitorizadas |
| `ff daemon-status` | Verificar estado do daemon |
| `ff service-install` | Instalar serviço systemd |

## Integração MCP

O FileFlow expõe um servidor MCP com 19 tools (status, duplicados, organizar, lixeira, pastas, regras, base de dados, antivírus, soft delete, daemon).

```bash
# Executar o servidor MCP isoladamente (stdio)
./venv/bin/python src/fileflow_mcp/server.py

# Executar via CLI
ff mcp-tools          # listar tools disponíveis
ff mcp-enable         # ativar MCP
ff mcp-disable        # desativar MCP
ff start --mcp        # iniciar monitoramento com MCP
```

Tools disponíveis: `fileflow_status`, `fileflow_scan_duplicates`, `fileflow_organize_preview`, `fileflow_organize_run`, `fileflow_trash_list`, `fileflow_trash_recover`, `fileflow_trash_clean`, `fileflow_watch_list`, `fileflow_watch_add`, `fileflow_watch_remove`, `fileflow_rules_list`, `fileflow_rule_add`, `fileflow_rule_remove`, `fileflow_db_info`, `fileflow_db_reset`, `fileflow_malware_scan_file`, `fileflow_malware_scan_dir`, `fileflow_delete`, `fileflow_daemon_status`.

Tools destrutivos (`fileflow_organize_run`, `fileflow_db_reset`) requerem `confirm=True`.

### Configuração

As definições MCP ficam em `~/.fileflow/mcp_config.json` (rate limit, tools bloqueadas, audit log).

```bash
ff mcp          # ver configuração MCP
ff mcp-audit    # ver audit log
```

## Stack

- Python 3.10+
- watchdog (monitoramento de ficheiros)
- SQLite (armazenamento do índice)
- Rich (UI de terminal)
- MCP SDK (integração com IA, FastMCP)