# Hyprland Beauty MCP Server

An MCP (Model Context Protocol) server that gives AI agents powerful tools to create, edit, and design beautiful **Hyprland**, **Waybar**, and related Wayland desktop configurations.

## What this server provides

- **Full embedded wiki references** for Hyprland (`https://wiki.hypr.land/`) and Waybar (`https://github.com/Alexays/Waybar`).
- **Beautiful config generators** for `hyprland.conf` and `waybar/config` + `style.css`.
- **Theme palette generator** for cohesive color schemes.
- **Syntax lookup tool** (`get_config_reference`) so the AI can quickly look up monitors, blur, shadows, window rules, layer rules, layouts, inputs, gestures, etc.
- **Template applier** for quick beautiful setups (modern-glass, catppuccin, tokyo-night, minimal-dark, archcraft-style).
- **Full beauty guide** combining all best practices, design checklists, and troubleshooting references.

## Installation

```bash
pip install mcp
python mcp_server.py
```

## How to use with an AI agent

Configure your MCP-compatible client (e.g., Claude Desktop, Claude Code, or any agent that supports MCP) to connect via stdio:

```json
{
  "mcpServers": {
    "hyprland-mcp": {
      "command": "python",
      "args": ["/home/user/hyprland-mcp/mcp_server.py"]
    }
  }
}
```

Then instruct the agent:

> "Use the hyprland-beauty MCP server. Create a beautiful modern-glass Hyprland config with purple accents for my dual-monitor setup, including waybar style. Reference the wiki as needed."

The agent will call tools like:
- `get_config_reference(query="monitor")`
- `generate_theme_palette()`
- `create_hyprland_config(...)`
- `create_waybar_config(...)`

## Key references embedded in the server

| Topic | URL |
|---|---|
| Official Hyprland Wiki | https://wiki.hypr.land/ |
| Config / Monitors | https://wiki.hypr.land/Configuring/Monitors/ |
| Config / Keywords | https://wiki.hypr.land/Configuring/Keywords/ |
| Config / Variables (blur/shadow) | https://wiki.hypr.land/Configuring/Variables/ |
| Config / Window Rules | https://wiki.hypr.land/Configuring/Window-Rules/ |
| Config / Layer Rules | https://wiki.hypr.land/Configuring/Layer-Rules/ |
| Config / Keyboard | https://wiki.hypr.land/Configuring/Keyboard/ |
| Config / Touchpad | https://wiki.hypr.land/Configuring/Touchpad/ |
| Config / Gestures | https://wiki.hypr.land/Configuring/Gestures/ |
| Plugins / Official | https://wiki.hypr.land/Plugins/Official/ |
| Plugins / Third-party | https://wiki.hypr.land/Plugins/ |
| Waybar (GitHub) | https://github.com/Alexays/Waybar |
| Archcraft Setup Guide | https://wiki.archcraft.io/docs/wayland-compositors/hyprland/ |

## Generated file locations (suggested by tools)

- `~/.config/hypr/hyprland.conf`
- `~/.config/waybar/config`
- `~/.config/waybar/style.css`
- Custom theme scripts in `~/.config/hypr/scripts/`

## Design philosophy

The server promotes:
- **Modern glass aesthetics**: blur, transparency, rounded borders, subtle shadows.
- **Consistent palettes**: same colors across Hyprland borders, Waybar modules, rofi, terminal, notifications.
- **Good typography**: Nerd Fonts, clean spacing, readable sizes.
- **Functional beauty**: every setting serves a purpose (input sensitivity, workspace swipe, floating rules, layer rules).

## Tools available

| Tool | Purpose |
|---|---|
| `create_hyprland_config` | Generate beautiful `hyprland.conf` |
| `create_waybar_config` | Generate `waybar/config` + `style.css` |
| `generate_theme_palette` | Generate cohesive color palette |
| `get_config_reference` | Look up syntax/reference for any Hyprland feature |
| `apply_config_template` | Apply quick theme templates to files |
| `get_full_beauty_guide` | Get complete design checklist and guide |

## Resources (read-only context)

- `knowledge://hyprland-wiki-reference`
- `knowledge://waybar-reference`
- `knowledge://beautiful-styling-guide`

## Prompt

- `beauty_config_prompt`: A ready-made prompt to instruct any AI agent using this server.
