#!/usr/bin/env python3
import json
import os
import subprocess
import re
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hyprland-mcp")

HYPRCTL = "hyprctl"
HYPRLAND_CONF = Path(os.path.expanduser("~/.config/hypr/hyprland.conf"))
HYPRLAND_WIKI = "https://wiki.hypr.land"
HYPRCTL_HELP = "https://wiki.hypr.land/Using-hyprctl"


def _run_hyprctl(args: list[str]) -> str:
    try:
        result = subprocess.run(
            [HYPRCTL] + args, capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return f"error: {result.stderr.strip() or result.stdout.strip()}"
        if "-j" in args:
            try:
                return json.dumps(json.loads(result.stdout), indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                pass
        return result.stdout.strip()
    except FileNotFoundError:
        return "error: hyprctl not found (not in Hyprland session?)"
    except subprocess.TimeoutExpired:
        return "error: hyprctl timed out"


def _parse_config_section(lines: list[str], section: str) -> dict:
    result = {}
    in_section = False
    depth = 0
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("$"):
            continue
        if "{" in stripped and section in stripped:
            in_section = True
            depth += stripped.count("{")
            continue
        if in_section:
            depth += stripped.count("{")
            depth -= stripped.count("}")
            if depth <= 0:
                break
            if "=" in stripped:
                key, _, val = stripped.partition("=")
                result[key.strip()] = val.strip()
    return result


# ------------------------------------------------------------------
# Knowledge resources
# ------------------------------------------------------------------

@mcp.resource("knowledge://hyprland-wiki")
def hyprland_wiki() -> str:
    return f"""Official Hyprland Wiki: {HYPRLAND_WIKI}
Wiki sections: Configuring/Monitors, Configuring/Keywords, Configuring/Variables,
Configuring/Window-Rules, Configuring/Layer-Rules, Configuring/Keyboard,
Configuring/Touchpad, Configuring/Gestures, Using-hyprctl
Dispatch docs: https://wiki.hypr.land/Configuring/Dispatchers"""


# ------------------------------------------------------------------
# Prompt
# ------------------------------------------------------------------

@mcp.prompt()
def hyprland_assistant() -> str:
    return """You are a Hyprland assistant. Use the tools to query and control Hyprland.
- Use hyprctl wrappers to get state, dispatch commands, change settings
- Use config tools to read/edit hyprland.conf
- Reference the Hyprland wiki when needed
- All changes via `hyprctl keyword` are temporary (lost on restart). To make permanent, edit hyprland.conf."""


# ------------------------------------------------------------------
# Tools — Query
# ------------------------------------------------------------------

@mcp.tool()
def hyprctl_raw(command: str) -> str:
    """Run any hyprctl command directly.
    Example: hyprctl_raw("monitors") or hyprctl_raw("-j monitors")
    """
    return _run_hyprctl(command.split())


@mcp.tool()
def get_monitors() -> str:
    """List all monitors with resolution, position, refresh rate, workspace."""
    return _run_hyprctl(["-j", "monitors"])


@mcp.tool()
def get_workspaces() -> str:
    """List all workspaces with window count, monitor, layout."""
    return _run_hyprctl(["-j", "workspaces"])


@mcp.tool()
def get_clients() -> str:
    """List all windows (clients) with class, title, workspace, position, size."""
    return _run_hyprctl(["-j", "clients"])


@mcp.tool()
def get_active_window() -> str:
    """Get the currently focused window details."""
    return _run_hyprctl(["-j", "activewindow"])


@mcp.tool()
def get_devices() -> str:
    """List all input devices (mice, keyboards, tablets, touch)."""
    return _run_hyprctl(["-j", "devices"])


@mcp.tool()
def get_binds() -> str:
    """List all keybinds."""
    return _run_hyprctl(["-j", "binds"])


@mcp.tool()
def get_option(option: str) -> str:
    """Get a specific config option value. Example: get_option("general:gaps_in")"""
    return _run_hyprctl(["-j", "getoption", option])


@mcp.tool()
def get_version() -> str:
    """Get Hyprland version and build info."""
    return _run_hyprctl(["version"])


@mcp.tool()
def get_splash() -> str:
    """Get the current random splash message."""
    return _run_hyprctl(["splash"])


@mcp.tool()
def get_layers() -> str:
    """List all layers in the compositor."""
    return _run_hyprctl(["-j", "layers"])


# ------------------------------------------------------------------
# Tools — Actions
# ------------------------------------------------------------------

@mcp.tool()
def dispatch(command: str) -> str:
    """Dispatch a Hyprland command. See dispatchers list below.
    Common dispatchers:
    workspace <name|id>        — switch to workspace
    movetoworkspace <name|id>  — move window + switch
    togglespecialworkspace     — toggle special workspace
    killactive                 — kill active window
    fullscreen <0|1>           — toggle fullscreen
    togglefloating             — toggle floating
    exec <command>             — run a command
    focusmonitor <name>        — focus a monitor
    movewindow <dir>           — move focus (l, r, u, d)
    resizeactive <x> <y>      — resize active window
    moveactive <x> <y>         — move active window
    cyclenext                  — cycle to next window
    split:ratio <float>        — change split ratio (0.1-0.9)
    pin                        — pin active window
    Example: dispatch("workspace 4") or dispatch("exec firefox")
    """
    return _run_hyprctl(["dispatch", command])


@mcp.tool()
def set_keyword(keyword: str, value: str) -> str:
    """Dynamically set a config keyword (temporary until restart).
    Example: set_keyword("general:gaps_in", "10")
             set_keyword("decoration:rounding", "0")
             set_keyword("bind", "SUPER, Q, killactive")
    """
    return _run_hyprctl(["keyword", keyword, value])


@mcp.tool()
def reload_config() -> str:
    """Reload hyprland.conf (applies changes without restart)."""
    return _run_hyprctl(["reload"])


@mcp.tool()
def notify(message: str, time_ms: int = 5000, icon: str = "") -> str:
    """Send a desktop notification via Hyprland.
    icon: Nerd Font icon or emoji
    """
    return _run_hyprctl(["notify", "-1", str(time_ms), "0", f"{icon} {message}"])


@mcp.tool()
def kill_window() -> str:
    """Enter kill mode (click a window to close it)."""
    return _run_hyprctl(["kill"])


# ------------------------------------------------------------------
# Tools — Config editing
# ------------------------------------------------------------------

@mcp.tool()
def read_config() -> str:
    """Read the current hyprland.conf file content."""
    if not HYPRLAND_CONF.exists():
        return f"error: config not found at {HYPRLAND_CONF}"
    return HYPRLAND_CONF.read_text()


@mcp.tool()
def get_config_section(section: str) -> str:
    """Parse and return a specific section from hyprland.conf.
    Example: get_config_section("general")
             get_config_section("decoration")
             get_config_section("input")
    """
    if not HYPRLAND_CONF.exists():
        return f"error: config not found at {HYPRLAND_CONF}"
    lines = HYPRLAND_CONF.read_text().splitlines()
    result = _parse_config_section(lines, section)
    if result:
        return json.dumps(result, indent=2)
    return f"section '{section}' not found or empty"


@mcp.tool()
def set_config_value(section: str, key: str, value: str) -> str:
    """Edit a specific value in hyprland.conf and reload.
    Example: set_config_value("general", "gaps_in", "10")
             set_config_value("decoration", "rounding", "16")
    Only updates the first matching section.
    """
    if not HYPRLAND_CONF.exists():
        return f"error: config not found at {HYPRLAND_CONF}"

    content = HYPRLAND_CONF.read_text()
    lines = content.splitlines()
    in_section = False
    depth = 0
    changed = False
    new_lines = []

    for line in lines:
        stripped = line.strip()
        if not in_section and "{" in stripped and section in stripped:
            in_section = True
            depth = stripped.count("{") - stripped.count("}")
            new_lines.append(line)
            continue
        if in_section:
            depth += stripped.count("{") - stripped.count("}")
            if not changed and "=" in stripped:
                k = stripped.split("=")[0].strip()
                if k == key:
                    indent = line[:len(line) - len(line.lstrip())]
                    new_lines.append(f"{indent}{key} = {value}")
                    changed = True
                    continue
            if depth <= 0:
                in_section = False
        new_lines.append(line)

    if not changed:
        return f"key '{key}' not found in section '{section}'"

    HYPRLAND_CONF.write_text("\n".join(new_lines))
    reload_result = _run_hyprctl(["reload"])
    return f"Updated {section}:{key} = {value}\nReload: {reload_result}"


@mcp.tool()
def add_config_line(line: str, after_section: str = None) -> str:
    """Append a line to hyprland.conf (or after a section) and reload.
    Example: add_config_line("bind = SUPER, W, exec, firefox")
             add_config_line('windowrulev2 = float, class:^(pavucontrol)$', after_section="windowrulev2")
    """
    if not HYPRLAND_CONF.exists():
        return f"error: config not found at {HYPRLAND_CONF}"

    content = HYPRLAND_CONF.read_text()
    if after_section:
        lines = content.splitlines()
        last_match = -1
        for i, l in enumerate(lines):
            if after_section in l and "=" in l and not l.strip().startswith("#"):
                last_match = i
        if last_match >= 0:
            lines.insert(last_match + 1, line)
            HYPRLAND_CONF.write_text("\n".join(lines))
        else:
            return f"pattern '{after_section}' not found"
    else:
        HYPRLAND_CONF.write_text(content.rstrip() + "\n" + line + "\n")

    reload_result = _run_hyprctl(["reload"])
    return f"Added: {line}\nReload: {reload_result}"


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
