# Hyprland MCP Server

MCP (Model Context Protocol) server for controlling Hyprland via AI agents.

Talk to Hyprland over `hyprctl` — query state, dispatch commands, change settings, edit config.

Requires running **inside a Hyprland session**.

## Tools

**Query:**
| Tool | What it does |
|---|---|
| `hyprctl_raw` | Run any hyprctl command |
| `get_monitors` | List monitors |
| `get_workspaces` | List workspaces |
| `get_clients` | List windows |
| `get_active_window` | Focused window details |
| `get_devices` | Input devices |
| `get_binds` | Keybinds |
| `get_option` | Any config option value |
| `get_version` | Hyprland version |
| `get_layers` | Compositor layers |

**Actions:**
| Tool | What it does |
|---|---|
| `dispatch` | Run a dispatcher (workspace, exec, kill, floating...) |
| `set_keyword` | Change a setting on the fly |
| `reload_config` | Reload hyprland.conf |
| `notify` | Send notification |
| `kill_window` | Kill-window mode |

**Config:**
| Tool | What it does |
|---|---|
| `read_config` | Read hyprland.conf |
| `get_config_section` | Parse a specific section |
| `set_config_value` | Edit a value + reload |
| `add_config_line` | Append a line + reload |

## Install

```bash
pip install mcp
python mcp_server.py
```

## opencode.jsonc

```json
{
  "hyprland-mcp": {
    "type": "local",
    "command": ["python", "-m", "mcp_server"],
    "env": { "PYTHONPATH": "/path/to/hyprland-mcp" },
    "enabled": true
  }
}
```

## Wiki

https://wiki.hypr.land/ — embedded as `knowledge://hyprland-wiki` resource.
