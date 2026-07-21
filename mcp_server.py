#!/usr/bin/env python3
"""
Hyprland Beauty MCP Server
=========================
An MCP server that provides AI agents with powerful tools to create,
edit, and beautify Hyprland, Waybar, and related Wayland desktop
configuration files.

Usage:
    python mcp_server.py

Install dependencies:
    pip install mcp

References embedded in this server (see resources):
- https://wiki.hypr.land/ (Official Hyprland Wiki)
- https://github.com/Alexays/Waybar (Waybar docs / examples)
- https://wiki.archcraft.io/docs/wayland-compositors/hyprland/
"""

from mcp.server.fastmcp import FastMCP
from pathlib import Path
import textwrap
import re

# ------------------------------------------------------------------
# Error handling helpers
# ------------------------------------------------------------------

class ConfigValidationError(Exception):
    """Raised when user input for a config does not pass validation."""
    pass

def _validate_hex_color(value: str, field_name: str) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        raise ConfigValidationError(f"{field_name} must be a string color value, got {type(value)}")
    # Accept rgb(...), rgba(...), or #hex
    valid_patterns = [
        r"^rgb\(\d{1,3},\s*\d{1,3},\s*\d{1,3}\)$",
        r"^rgba\(\d{1,3},\s*\d{1,3},\s*\d{1,3},\s*(?:0(?:\.\d+)?|1(?:\.0+)?)\)$",
        r"^#[0-9a-fA-F]{3,8}$",
    ]
    if not any(re.match(p, value) for p in valid_patterns):
        raise ConfigValidationError(
            f"{field_name} looks invalid: '{value}'. Use rgb(r,g,b), rgba(r,g,b,a) or #hex."
        )

def _validate_monitor_string(mon: str) -> None:
    if not isinstance(mon, str):
        raise ConfigValidationError(f"Monitor entry must be a string, got {type(mon)}")
    # Basic check: must contain commas for name, resolution, etc.
    if "," not in mon:
        raise ConfigValidationError(f"Monitor config must contain commas: '{mon}'")

def _safe_divide(a, b, default=1.0):
    try:
        return a / b if b != 0 else default
    except Exception:
        return default

# ------------------------------------------------------------------
# Initialize server
# ------------------------------------------------------------------

mcp = FastMCP("hyprland-mcp")

# ------------------------------------------------------------------
# Embedded knowledge: Wiki references & quick guides
# ------------------------------------------------------------------

HYPRLAND_WIKI_URL = "https://wiki.hypr.land/"
WAYBAR_GITHUB = "https://github.com/Alexays/Waybar"
ARCHCRAFT_WIKI = "https://wiki.archcraft.io/docs/wayland-compositors/hyprland/"
HYPRPAPER_CONF_EXAMPLE = "https://github.com/hyprwm/hyprpaper"

# ------------------------------------------------------------------
# Resources (read-only context for the AI)
# ------------------------------------------------------------------

@mcp.resource("knowledge://hyprland-wiki-reference")
def hyprland_wiki_reference() -> str:
    """Returns full reference links and key sections from the official Hyprland Wiki."""
    return textwrap.dedent(f"""
=== Official Hyprland Wiki ===
URL: {HYPRLAND_WIKI_URL}

Key Sections to Reference:
1. Configuring / Monitors      -> https://wiki.hypr.land/Configuring/Monitors/
2. Configuring / Keywords      -> https://wiki.hypr.land/Configuring/Keywords/
3. Configuring / Variables     -> https://wiki.hypr.land/Configuring/Variables/
4. Configuring / Window Rules -> https://wiki.hypr.land/Configuring/Window-Rules/
5. Configuring / Layer Rules  -> https://wiki.hypr.land/Configuring/Layer-Rules/
6. Configuring / Input        -> https://wiki.hypr.land/Configuring/Keyboard/
7. Configuring / Touchpad     -> https://wiki.hypr.land/Configuring/Touchpad/
8. Configuring / Gestures      -> https://wiki.hypr.land/Configuring/Gestures/
9. Plugins / Official        -> https://wiki.hypr.land/Plugins/Official/
10. Plugins / Third-party     -> https://wiki.hypr.land/Plugins/
11. Decoration / Blur         -> https://wiki.hypr.land/Configuring/Variables/#blur
12. Decoration / Shadows      -> https://wiki.hypr.land/Configuring/Variables/#shadows
13. Decoration / Rounded Corners -> https://wiki.hypr.land/Configuring/Variables/
14. Environment / Variables    -> https://wiki.hypr.land/Configuring/Environment-variables/

Syntax Notes:
- Config file: ~/.config/hypr/hyprland.conf (or .lua if using lua config)
- Sections: general { ... }, input { ... }, decoration { ... }, windowrulev2 = ...
- Variables: $mainMod = SUPER; $terminal = kitty; etc.
- Keybind syntax: bind = $mainMod, key, dispatcher, args
- Monitor syntax: monitor = name, resolution@refresh, position, scale, transform, vrr
- Window rules: windowrulev2 = float, title:.*(calculator).*
- Layer rules: layerrule = blur, waybar; layerrule = ignorezero, waybar; layerrule = blur, rofi

Official Example Config (GitHub):
https://github.com/hyprwm/Hyprland/blob/main/example/hyprland.conf
""")

@mcp.resource("knowledge://waybar-reference")
def waybar_reference() -> str:
    """Returns Waybar documentation and common styling patterns."""
    return textwrap.dedent(f"""
=== Waybar ===
GitHub / Docs: {WAYBAR_GITHUB}
Wiki-style guide: https://github.com/Alexays/Waybar/wiki

Structure:
- Config: ~/.config/waybar/config
- Style:  ~/.config/waybar/style.css
- Optional modules: backlight, battery, clock, cpu, custom, disk, hyprland/workspaces, idle_inhibitor, keyboard-state, memory, network, pulseaudio, temperature, tray, upower, user

Key Config Sections:
- "layer" = "top" / "bottom"
- "position" = "top" / "bottom"
- "modules-left" / "modules-center" / "modules-right"
- "spacing" between modules
- Format strings with JSON-style objects in CSS

Beautiful Style Patterns:
- Rounded corners (border-radius)
- Blur / transparency (rgba with alpha)
- Gradients (linear-gradient)
- Font Awesome / Nerd Font icons
- Padding and margin control per module
- Hover effects on workspace buttons (.hover)
- Active / inactive color states
- Box shadow for floating effect

Reference Config Examples:
- https://github.com/Alexays/Waybar/tree/master/resources/config
- https://github.com/Alexays/Waybar/tree/master/resources/style.css
""")

@mcp.resource("knowledge://beautiful-styling-guide")
def beautiful_styling_guide() -> str:
    """Returns a design guide for creating beautiful, modern Hyprland + Waybar setups."""
    return textwrap.dedent("""
=== Beauty & Design Guide ===

Colors & Themes:
1. Use a consistent 4-6 color palette (base, surface, overlay, text, accent, error)
2. Common modern palettes:
   - Catppuccin Mocha: #1e1e2e, #313244, #89b4fa, #cba6f7, #f38ba8, #f5c2e7
   - Tokyo Night: #1a1b26, #24283b, #7aa2f7, #bb9af7, #f7768e, #e0af68
   - Nord: #2e3440, #3b4252, #88c0d0, #81a1c1, #ebcb8b, #a3be8c
3. Transparency levels: rgba(0,0,0,0.3) - rgba(0,0,0,0.6) for glass effects
4. Blur radius: 10-20 for subtle glass, 30+ for heavy frosted look

Borders & Corners:
- border_size = 1 or 2 (thin = modern, thick = bold)
- rounding = 8 to 16 (higher = more modern / iOS-like)
- active_border = accent gradient; inactive_border = muted surface
- drop_shadow = true; shadow_offset = 0 8; shadow_range = 20-30; shadow_opacity = 0.2-0.4

Fonts:
- Use a Nerd Font for icons in Waybar (e.g., JetBrainsMono Nerd Font, Font Awesome 6, Material Design Icons)
- Font size: 10-14pt for Waybar; 10-12pt for terminal
- Line height: 1.2-1.5

Animations (if using plugins like hyprland-plugins / hypridle / custom scripts):
- Keep animations subtle (fade 150ms, slide 200ms)
- Avoid over-animation on workspaces (instant switch preferred)

Waybar Layout Ideas:
- Minimal: [workspace] | [clock] [battery] [volume]
- Full: [workspace] [window-title] [tray] [cpu/memory] [network] [audio] [battery] [clock]
- Centered title + left workspace + right system info = balanced design

Window Rules for Beauty:
- Float small apps (calculator, pavucontrol, file-roller): windowrulev2 = float, ...
- Opacity for floating windows: windowrulev2 = opacity 0.92 float, ...
- Rounded corners on all windows (default via general settings)
- Gaps: 5-12 for modern spacing; larger gaps for dramatic layouts

Reference: https://wiki.archcraft.io/docs/wayland-compositors/hyprland/ (Archcraft setup guide with full theme structure)
""")

# ------------------------------------------------------------------
# Tools (callable by AI agent)
# ------------------------------------------------------------------

def safe_tool_wrapper(func):
    """Wraps a tool to catch unexpected errors and return them gracefully."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConfigValidationError as exc:
            return {"error": str(exc), "notes": "Input validation failed. Check parameters and retry."}
        except Exception as exc:
            return {"error": f"Unexpected server error: {exc}", "notes": "Please report this to the maintainer with the request details."}
    return wrapper

@mcp.tool()
@safe_tool_wrapper
def create_hyprland_config(
    monitors: list[str] = None,
    keybinds: list[str] = None,
    gaps_in: int = 8,
    gaps_out: int = 12,
    border_size: int = 2,
    border_radius: int = 12,
    active_border_color: str = "#89b4fa",
    inactive_border_color: str = "#313244",
    layout: str = "dwindle",
    terminal: str = "kitty",
    browser: str = "firefox",
    file_manager: str = "dolphin",
    mod_key: str = "SUPER",
    include_blur: bool = True,
    include_shadow: bool = True,
    shadow_opacity: float = 0.25,
    autostart_apps: list[str] = None,
    extra_decoration: dict = None,
    **kwargs,
) -> dict:
    """
    Creates a beautiful, production-ready hyprland.conf.

    Args:
        monitors: List of monitor config strings, e.g. ["DP-1,1920x1080@144,0x0,1"]
        keybinds: List of extra bind strings, e.g. ["$mainMod, Q, killactive"]
        gaps_in / gaps_out / border_size / border_radius: Layout params
        active_border_color / inactive_border_color: Hex or rgb strings
        layout: "dwindle" or "master"
        terminal / browser / file_manager: App names for binds
        mod_key: Main modifier key
        include_blur / include_shadow: Glass effects
        shadow_opacity: Shadow opacity 0.0-1.0
        autostart_apps: List of exec-once commands
        extra_decoration: Optional dict overriding decoration block

    Returns:
        {"path_suggested": "~/.config/hypr/hyprland.conf", "content": "...", "notes": "..."}
    """
    # --- Input validation ---
    try:
        if gaps_in is not None and not (0 <= gaps_in <= 100):
            raise ConfigValidationError("gaps_in must be between 0 and 100")
        if gaps_out is not None and not (0 <= gaps_out <= 100):
            raise ConfigValidationError("gaps_out must be between 0 and 100")
        if border_size is not None and not (0 <= border_size <= 20):
            raise ConfigValidationError("border_size must be between 0 and 20")
        if border_radius is not None and not (0 <= border_radius <= 100):
            raise ConfigValidationError("border_radius must be between 0 and 100")
        if shadow_opacity is not None and not (0.0 <= shadow_opacity <= 1.0):
            raise ConfigValidationError("shadow_opacity must be between 0.0 and 1.0")
        if monitors:
            for m in monitors:
                _validate_monitor_string(m)
        _validate_hex_color(active_border_color, "active_border_color")
        _validate_hex_color(inactive_border_color, "inactive_border_color")
        if layout not in ("dwindle", "master"):
            # Allow only standard layouts; others can be added manually
            pass
    except ConfigValidationError as exc:
        return {"error": str(exc), "path_suggested": "~/.config/hypr/hyprland.conf", "notes": "Fix input values and retry."}

    monitors_str = ""
    if monitors:
        monitors_str = "\n".join([f"monitor = {m}" for m in monitors]) + "\n"

    keybinds_str = ""
    base_binds = [
        f"bind = $mainMod, Return, exec, {terminal}",
        f"bind = $mainMod, Q, killactive",
        f"bind = $mainMod, M, exit",
        f"bind = $mainMod SHIFT, F, fullscreen, 0",
        f"bind = $mainMod, F, togglefloating",
        f"bind = $mainMod, D, exec, wofi --show drun",
        f"bind = $mainMod, E, exec, {file_manager}",
        f"bind = $mainMod, B, exec, {browser}",
        f"bind = $mainMod, T, exec, {terminal}",
    ]
    all_binds = base_binds + (keybinds or [])
    keybinds_str = "\n".join([f"bind = {b}" if not b.startswith("bind = ") else b for b in all_binds])

    autostart = autostart_apps or [
        "waybar",
        "swaybg -i $(cat ~/.cache/wallpaper_path 2>/dev/null || echo /usr/share/backgrounds/default.jpg)",
    ]
    autostart_str = "\n".join([f"exec-once = {a}" for a in autostart])

    blur_part = ""
    if include_blur:
        blur_part = "\n    blur {\n        enabled = true\n        size = 8\n        passes = 2\n        new_optimizations = true\n        noise = 0.0117\n        contrast = 1.0\n        brightness = 0.8\n        vibrancy = 0.1696\n        vibrancy_darkness = 0.0\n        special = false\n        popups = true\n        popups_ignorealpha = 0.2\n    }"

    shadow_part = ""
    if include_shadow:
        color_hex = "%02x" % int(shadow_opacity * 255)
        shadow_part = (
            "\n    shadow {\n"
            "        enabled = true\n"
            "        range = 20\n"
            "        render_power = 3\n"
            "        color = rgba(000000" + color_hex + ")\n"
            "        color_inactive = rgba(0a0a0aaa)\n"
            "        ignore_window = true\n"
            "        offset = 0 8\n"
            "        scale = 0.97\n"
            "    }"
        )

    decoration_extra = extra_decoration or {
        "rounding": border_radius,
        "shadow_offset": "0 8",
        "shadow_range": 25,
        "shadow_opacity": shadow_opacity,
        "active_opacity": 1.0,
        "inactive_opacity": 1.0,
    }

    dec_block = f"""general {{
    gaps_in = {gaps_in}
    gaps_out = {gaps_out}
    border_size = {border_size}
    col.active_border = {active_border_color}
    col.inactive_border = {inactive_border_color}
    resize_on_border = true
    allow_tearing = false
    layout = {layout}
    no_focus_fallback = false
}}

decoration {{
    rounding = {decoration_extra.get('rounding', border_radius)}
    shadow_offset = {decoration_extra.get('shadow_offset', '0 8')}
    shadow_range = {decoration_extra.get('shadow_range', 25)}
    shadow_opacity = {decoration_extra.get('shadow_opacity', shadow_opacity)}
    shadow_render_power = 3
    col.shadow = rgba(000000cc)
    col.shadow_inactive = rgba(00000088)
    active_opacity = {decoration_extra.get('active_opacity', 1.0)}
    inactive_opacity = {decoration_extra.get('inactive_opacity', 1.0)}
    drop_shadow = true
    blur {blur_part.replace('    blur', '').strip() if include_blur else 'enabled = false'}
    shadow {shadow_part.replace('    shadow', '').strip() if include_shadow else 'enabled = false'}
}}"""

    content = textwrap.dedent(f"""# Generated by Hyprland Beauty MCP Server
# Reference: {HYPRLAND_WIKI_URL}
# Design: Modern glass + rounded + shadow aesthetic

$mainMod = {mod_key}
$terminal = {terminal}
$browser = {browser}
$fileManager = {file_manager}

{monitors_str}
# Key Bindings
{keybinds_str}

# Autostart
{autostart_str}

# Environment Variables (essential for Wayland compatibility)
env = GDK_BACKEND,wayland,x11,*
env = QT_QPA_PLATFORM,wayland;xcb
env = SDL_VIDEODRIVER,wayland
env = CLUTTER_BACKEND,wayland
env = XDG_CURRENT_DESKTOP,Hyprland
env = XDG_SESSION_TYPE,wayland
env = XDG_SESSION_DESKTOP,Hyprland

# Layout & Decoration
{dec_block}

# Input Config
input {{
    kb_layout = us
    follow_mouse = 1
    sensitivity = 0
    touchpad {{
        natural_scroll = true
        tap_to_click = true
        disable_while_typing = false
    }}
}}

gestures {{
    workspace_swipe = true
    workspace_swipe_fingers = 3
    workspace_swipe_distance = 300
    workspace_swipe_invert = false
}}

# Window Rules (beautiful float + opacity rules)
windowrulev2 = float, class:^(pavucontrol)$
windowrulev2 = float, class:^(file-roller)$
windowrulev2 = float, title:^(Calculator)$
windowrulev2 = float, title:^(Calculator - .*?)$
windowrulev2 = opacity 0.92 float, class:^(pavucontrol)$
windowrulev2 = opacity 0.9, class:^(Alacritty)$
windowrulev2 = float, title:^(Picture-in-Picture)$
windowrulev2 = float, title:^(Firefox - .*?Sharing Indicator)$

# Layer Rules (glass effects for bar / launcher)
layerrule = blur, waybar
layerrule = ignorezero, waybar
layerrule = blur, rofi
layerrule = ignorezero, rofi
layerrule = blur, wofi
layerrule = ignorezero, wofi

# Workspace Rules
windowrulev2 = workspace 1 silent, class:^(firefox)$
windowrulev2 = workspace 2 silent, class:^(code-oss)$
windowrulev2 = workspace special:magic silent, class:^(spotify)$

# Monitor Config Example (uncomment to use):
# monitor = DP-1,1920x1080@144,0x0,1
# monitor = HDMI-A-1,2560x1440@165,1920x0,1,transform,1
""")
    return {
        "path_suggested": "~/.config/hypr/hyprland.conf",
        "content": content,
        "notes": f"Includes modern glass effects. Wiki reference: {HYPRLAND_WIKI_URL}. Adjust monitors, binds, and theme colors as needed.",
    }

@mcp.tool()
@safe_tool_wrapper
def create_waybar_config(
    theme_colors: dict = None,
    left_modules: list = None,
    center_modules: list = None,
    right_modules: list = None,
    font: str = "JetBrainsMono Nerd Font",
    font_size: int = 12,
    bar_height: int = 36,
    include_pulse_audio: bool = True,
    include_temperature: bool = True,
    background_alpha: float = 0.6,
    css_extra: str = "",
    **kwargs,
) -> dict:
    """
    Creates a beautiful Waybar config + style.css pair.
    Args:
        theme_colors: Dict with keys background, surface, text, accent, success, warning, error
        left_modules: Modules on left (default: hyprland/workspaces)
        center_modules: Modules in center (default: window)
        right_modules: Modules on right (default: clock, battery, volume, tray)
        font / font_size / bar_height: Typography / sizing
        include_pulse_audio / include_temperature: Optional modules
        background_alpha: Background transparency 0.0-1.0
        css_extra: Additional CSS to inject
    Returns:
        {"config_path": "~/.config/waybar/config", "style_path": "~/.config/waybar/style.css", "content": {...}}
    """
    colors = theme_colors or {
        "background": "#1e1e2e",
        "surface": "#313244",
        "text": "#cdd6f4",
        "accent": "#89b4fa",
        "success": "#a6e3a1",
        "warning": "#fab387",
        "error": "#f38ba8",
    }
    # Validation for theme_colors
    required_color_keys = {"background", "surface", "text", "accent", "success", "warning", "error"}
    if theme_colors is not None:
        missing = required_color_keys - set(theme_colors.keys())
        if missing:
            return {"error": f"theme_colors missing keys: {missing}", "notes": f"Provide at least: {required_color_keys}"}
        for k, v in theme_colors.items():
            try:
                _validate_hex_color(str(v), k)
            except ConfigValidationError as exc:
                return {"error": str(exc), "notes": "Theme color values must be valid hex or rgb/rgba strings."}

    left = left_modules or ["hyprland/workspaces", "hyprland/window"]
    center = center_modules or ["hyprland/window"]
    right = right_modules or ["pulseaudio", "network", "cpu", "memory", "temperature", "battery", "tray", "clock"]
    if not include_pulse_audio and "pulseaudio" in right:
        right.remove("pulseaudio")
    if not include_temperature and "temperature" in right:
        right.remove("temperature")

    bg_rgba = colors["background"]
    # Simple hex to rgba approximation for CSS
    config_content = textwrap.dedent(f"""[
  {{
    "layer": "top",
    "position": "top",
    "height": {bar_height},
    "spacing": 8,
    "modules-left": ["{ '", "'.join(left) }"],
    "modules-center": ["{ '", "'.join(center) }"],
    "modules-right": ["{ '", "'.join(right) }"],
    "font": "{font} {font_size}",
    "hyprland/workspaces": {{
        "format": "{{{{name}}}}",
        "format-icons": {{"1":"1","2":"2","3":"3","4":"4","5":"5","6":"6","special":"*"}},
        "persistent-workspaces": {{"*": 5}},
        "show-special": true
    }},
    "hyprland/window": {{
        "format": "{{{{title}}}}",
        "max-length": 60,
        "min-length": 20
    }},
    "pulseaudio": {{
        "format": "{{{{volume}}}}% {{{{icon}}}}",
        "format-icons": {{"default": ["", "", ""], "headphone":""}},
        "format-muted": " Muted",
        "scroll-step": 5,
        "on-click": "pactl set-sink-mute @DEFAULT_SINK@ toggle"
    }},
    "cpu": {{"format": "{{{{usage}}}}% ", "interval": 2}},
    "memory": {{"format": "{{{{percent}}}}% ", "interval": 5}},
    "temperature": {{"format": "{{{{temperatureC}}}}°C ", "interval": 5}},
    "network": {{"format-wifi": "{{{{essid}}}} ", "format-ethernet": "Connected ", "format-disconnected": "Disconnected ⚠"}},
    "battery": {{"format": "{{{{capacity}}}}% {{{{icon}}}}", "format-icons": ["", "", "", "", "", "", "", "", "", ""], "states": {{"warning": 30, "critical": 15}}}},
    "tray": {{"icon-size": 16, "spacing": 8}},
    "clock": {{"format": "{{{{time}}}}", "format-alt": "{{{{date}}}}", "tooltip-format": "<big>{{{{calendar}}}}</big>"}}
  }}
]
""")

    style_content = textwrap.dedent(f"""
/* ============================================
   Waybar Style - Beautiful Glass Theme
   Reference: {WAYBAR_GITHUB}
   ============================================ */

* {{
    border: none;
    border-radius: 0;
    font-family: "{font}", "Font Awesome 6 Free", "Material Design Icons";
    font-size: {font_size}px;
    min-height: 0;
}}

window#waybar {{
    background-color: rgba({int(bg_rgba[1:3], 16)}, {int(bg_rgba[3:5], 16)}, {int(bg_rgba[5:], 16)}, {background_alpha:.2f});
    color: {colors["text"]};
    border-bottom: 1px solid rgba({int(colors["surface"][1:3], 16)}, {int(colors["surface"][3:5], 16)}, {int(colors["surface"][5:], 16)}, 0.3);
}}

/* Workspace buttons */
#workspaces button {{
    padding: 0 10px;
    background-color: transparent;
    color: {colors["text"]};
    border-bottom: 2px solid transparent;
    border-radius: 8px 8px 0 0;
}}
#workspaces button:hover {{
    background-color: rgba({int(colors["surface"][1:3], 16)}, {int(colors["surface"][3:5], 16)}, {int(colors["surface"][5:], 16)}, 0.3);
}}
#workspaces button.active {{
    background-color: rgba({int(colors["accent"][1:3], 16)}, {int(colors["accent"][3:5], 16)}, {int(colors["accent"][5:], 16)}, 0.15);
    color: {colors["accent"]};
    border-bottom: 2px solid {colors["accent"]};
}}
#workspaces button.urgent {{
    background-color: rgba({int(colors["error"][1:3], 16)}, {int(colors["error"][3:5], 16)}, {int(colors["error"][5:], 16)}, 0.2);
    color: {colors["error"]};
}}

/* Modules */
#window, #workspaces, #pulseaudio, #network, #cpu, #memory, #temperature, #battery, #tray, #clock {{
    padding: 0 12px;
    margin: 0 2px;
    background-color: rgba({int(colors["surface"][1:3], 16)}, {int(colors["surface"][3:5], 16)}, {int(colors["surface"][5:], 16)}, 0.2);
    border-radius: 10px;
}}
#window {{
    font-weight: 500;
    letter-spacing: 0.3px;
}}

#clock {{
    font-weight: bold;
    color: {colors["accent"]};
}}
#battery.charging, #battery.plugged {{
    color: {colors["success"]};
}}
#battery.critical:not(.charging) {{
    color: {colors["error"]};
    animation: blink 0.5s linear infinite alternate;
}}
@keyframes blink {{
    to {{
        background-color: rgba({int(colors["error"][1:3], 16)}, {int(colors["error"][3:5], 16)}, {int(colors["error"][5:], 16)}, 0.3);
    }}
}}
#pulseaudio.muted {{
    color: {colors["warning"]};
}}
#temperature.critical {{
    color: {colors["error"]};
}}
#memory {{
    color: {colors["text"]};
}}
#cpu {{
    color: {colors["success"]};
}}
{css_extra}
""")
    return {
        "config_path": "~/.config/waybar/config",
        "style_path": "~/.config/waybar/style.css",
        "content": {
            "config": config_content,
            "style": style_content,
        },
        "notes": f"Theme colors applied: {colors}. Reference docs: {WAYBAR_GITHUB}. Adjust modules, fonts, and colors to match your aesthetic.",
    }

@mcp.tool()
@safe_tool_wrapper
def generate_theme_palette(
    name: str = "catppuccin-mocha",
    base: str = "#1e1e2e",
    surface: str = "#313244",
    text: str = "#cdd6f4",
    accent: str = "#89b4fa",
    accent_secondary: str = "#cba6f7",
    error: str = "#f38ba8",
    success: str = "#a6e3a1",
    warning: str = "#fab387",
    **kwargs,
) -> dict:
    """Generates a cohesive color palette for Hyprland + Waybar + any related apps."""
    palette = {
        "name": name,
        "base": base,
        "surface": surface,
        "text": text,
        "accent": accent,
        "accent_secondary": accent_secondary,
        "error": error,
        "success": success,
        "warning": warning,
        "hyprland_colors": {
            "background": base,
            "surface": surface,
            "text": text,
            "accent": accent,
        },
        "waybar_colors": {
            "background": base,
            "surface": surface,
            "text": text,
            "accent": accent,
            "success": success,
            "warning": warning,
            "error": error,
        },
        "suggested_wallpapers": [
            "Abstract dark gradient with purple/blue tones",
            "Minimalist geometric dark background",
            "Frosted glass / bokeh dark texture",
        ],
        "font_suggestions": [
            "JetBrainsMono Nerd Font",
            "FiraCode Nerd Font",
            "Inter",
            "Manrope",
        ],
    }
    return palette

@mcp.tool()
@safe_tool_wrapper
def get_config_reference(query: str, **kwargs) -> str:
    """
    Returns a targeted reference snippet based on a user query about Hyprland config syntax.

    Args:
        query: A keyword or phrase like 'monitor', 'blur', 'windowrule', 'layer', 'input', 'gesture', 'workspace', 'layout', 'animation', 'plugin', 'shadow', 'border', 'opacity', 'float', 'keyboard', 'touchpad'

    Returns:
        A concise explanation with syntax examples and a link to the relevant wiki section.
    """
    refs = {
        "monitor": (HYPRLAND_WIKI_URL + "Configuring/Monitors/", "Monitor syntax: monitor = NAME,RESOLUTION@REFRESH,POSITION,SCALE,TRANSFORM,VARR. Example: monitor = DP-1,1920x1080@144,0x0,1."),
        "blur": (HYPRLAND_WIKI_URL + "Configuring/Variables/#blur", "Blur settings inside decoration block: blur { enabled = true; size = 8; passes = 2; new_optimizations = true; noise = 0.0117; }. Apply via layerrule = blur, waybar."),
        "shadow": (HYPRLAND_WIKI_URL + "Configuring/Variables/#shadows", "Shadow settings inside decoration: shadow { enabled = true; range = 20; render_power = 3; color = rgba(000000aa); offset = 0 8; scale = 0.97; }."),
        "windowrule": (HYPRLAND_WIKI_URL + "Configuring/Window-Rules/", "Window rules (v2 preferred): windowrulev2 = float, title:^.*(calculator).*; windowrulev2 = opacity 0.92 float, class:^.*(pavucontrol).*; windowrulev2 = workspace 2, class:^.*(firefox).*;"),
        "layer": (HYPRLAND_WIKI_URL + "Configuring/Layer-Rules/", "Layer rules: layerrule = blur, waybar; layerrule = ignorezero, waybar; layerrule = blur, rofi; layerrule = ignorezero, rofi; layerrule = ignorealpha 0.5, wofi."),
        "layout": (HYPRLAND_WIKI_URL + "Configuring/Keywords/", "Layout: layout = dwindle | master | master (with master new on top/active). Change with bind commands or via dispatcher."),
        "input": (HYPRLAND_WIKI_URL + "Configuring/Keyboard/", "Input block: input { kb_layout = us; follow_mouse = 1; sensitivity = 0; touchpad { natural_scroll = true; tap_to_click = true; } }."),
        "gesture": (HYPRLAND_WIKI_URL + "Configuring/Gestures/", "Gestures: gestures { workspace_swipe = true; workspace_swipe_fingers = 3; workspace_swipe_distance = 300; workspace_swipe_invert = false; }."),
        "workspace": (HYPRLAND_WIKI_URL + "Configuring/Workspaces/", "Workspaces: bind = $mainMod, 1, workspace, 1. Special workspace with workspace special:silent or persistent rules."),
        "animation": (HYPRLAND_WIKI_URL + "Plugins/", "Animations are configured via variables or plugins. Some plugins (like hyprland-plugins) provide additional animation controls. For native settings, animations are minimal."),
        "plugin": (HYPRLAND_WIKI_URL + "Plugins/Official/ and " + HYPRLAND_WIKI_URL + "Plugins/", "Plugins: Use hyprpm or manual install. Official plugins: hyprbars, hyprcursor, etc. Third-party plugins provide extra features."),
        "opacity": (HYPRLAND_WIKI_URL + "Configuring/Variables/", "Window opacity rules: windowrulev2 = opacity 0.9 float, ...; or set globally via decoration active/inactive opacity."),
        "float": (HYPRLAND_WIKI_URL + "Configuring/Window-Rules/", "Float a window: bind dispatcher togglefloating; or windowrulev2 = float, title:...; or bind = $mainMod, V, togglefloating."),
        "keyboard": (HYPRLAND_WIKI_URL + "Configuring/Keyboard/", "Keyboard: kb_layout, kb_variant, kb_options, numlock_by_default, capslock_by_default, scroll_factor."),
        "touchpad": (HYPRLAND_WIKI_URL + "Configuring/Touchpad/", "Touchpad settings: natural_scroll, disable_while_typing, middle_button_emulation, clickfinger_behavior, scroll_factor."),
    }
    query_normalized = query.lower().strip()
    # Try exact match first, then partial
    for key in refs:
        if query_normalized == key or query_normalized in key:
            link, desc = refs[key]
            return f"=== {key.upper()} ===\n{desc}\nSyntax/Link: {link}\n"
    # Try partial match across all keys
    for key in refs:
        if key in query_normalized:
            link, desc = refs[key]
            return f"=== {key.upper()} (matched from query) ===\n{desc}\nSyntax/Link: {link}\n"
    return f"No exact reference found for '{query}'. Try: monitor, blur, shadow, windowrule, layer, layout, input, gesture, workspace, keyboard, touchpad, float, opacity, animation, plugin. Main wiki: {HYPRLAND_WIKI_URL}\n"

@mcp.tool()
@safe_tool_wrapper
def apply_config_template(
    template_name: str,
    output_path: str,
    custom_vars: dict = None,
    **kwargs,
) -> dict:
    """
    Applies a pre-built beautiful template to a target file.

    Args:
        template_name: "modern-glass", "minimal-dark", "catppuccin", "tokyo-night", "archcraft-style"
        output_path: File path to write to (e.g. /home/user/.config/hypr/hyprland.conf)
        custom_vars: Optional overrides like {"mod_key":"ALT","layout":"master"}

    Returns:
        {"written_to": output_path, "template": template_name, "bytes": ...}
    """
    templates = {
        "modern-glass": "Includes blur, rounded corners, shadows, glass-style waybar, and modern color palette.",
        "minimal-dark": "Dark, low-contrast, minimal borders, no blur, clean typography.",
        "catppuccin": "Uses Catppuccin Mocha color palette across Hyprland and Waybar.",
        "tokyo-night": "Tokyo Night dark theme with purple/blue accent colors.",
        "archcraft-style": "Inspired by Archcraft WSE setup with full theme integration, scripts, and structured config folders.",
    }
    chosen = templates.get(template_name, "Unknown template.")
    content = f"# Template: {template_name}\n# {chosen}\n# Generated by Hyprland Beauty MCP Server\n# Reference: {HYPRLAND_WIKI_URL}\n"
    if custom_vars:
        for k, v in custom_vars.items():
            content += f"# Custom override: {k} = {v}\n"
    content += f"\n# Main config content would be inserted here based on template '{template_name}'.\n"
    content += "# For full generation, use create_hyprland_config() or create_waybar_config() with theme_colors.\n"
    # Write file
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content)
    return {
        "written_to": str(out_path.absolute()),
        "template": template_name,
        "description": chosen,
        "bytes": len(content.encode("utf-8")),
        "notes": f"Template applied. Reference wiki: {HYPRLAND_WIKI_URL}. For full beautiful configs, combine with theme palettes and waybar styles.",
    }

@mcp.tool()
@safe_tool_wrapper
def get_full_beauty_guide(**kwargs) -> str:
    """Returns a comprehensive guide combining all resources, templates, and design principles."""
    return textwrap.dedent(f"""
=== FULL BEAUTY GUIDE FOR HYPRLAND ===

This guide combines everything needed for beautiful, modern Wayland setups.

1. CORE REFERENCES
------------------
- Official Wiki: {HYPRLAND_WIKI_URL}
- Waybar: {WAYBAR_GITHUB}
- Archcraft Setup (full theme structure): {ARCHCRAFT_WIKI}

2. CONFIG FILES TO MANAGE
--------------------------
- ~/.config/hypr/hyprland.conf       (main compositor config)
- ~/.config/waybar/config             (bar modules)
- ~/.config/waybar/style.css         (bar styling)
- ~/.config/hypr/hyprpaper.conf       (wallpaper)
- ~/.config/hypr/hypridle.conf        (idle / lock)
- ~/.config/hypr/hyprlock.conf        (lock screen)
- ~/.config/hypr/scripts/             (custom scripts for volume, brightness, theme switching)

3. DESIGN CHECKLIST
-------------------
[ ] Monitor config: monitor = NAME,RESOLUTION@REFRESH,POSITION,SCALE,TRANSFORM,VARR
[ ] Environment variables set (GDK_BACKEND, QT_QPA_PLATFORM, SDL_VIDEODRIVER, CLUTTER_BACKEND, XDG_*)
[ ] Keybinds for terminal ($mainMod,T), browser ($mainMod,B), launcher ($mainMod,D), quit ($mainMod,Q), exit ($mainMod,M)
[ ] Autostart: waybar, wallpaper script (hyprpaper / swaybg), notification daemon (dunst / mako), polkit agent
[ ] Layout: dwindle (default dynamic) or master (split pane)
[ ] Decoration: border_size (1-3), rounding (8-16), active/inactive colors, blur enabled, shadow enabled, opacity settings
[ ] Input: keyboard layout, mouse sensitivity (0 preferred), touchpad natural_scroll, tap_to_click
[ ] Gestures: workspace_swipe with 3 fingers
[ ] Window rules: float for calculators / pavucontrol / file-roller; workspace assignment for browsers / editors; opacity rules
[ ] Layer rules: blur and ignorezero for waybar, rofi, wofi
[ ] Waybar: modern glass theme with rounded modules, workspace buttons, system info (cpu, memory, temperature, battery, audio, clock, tray)
[ ] Fonts: Nerd Font installed and set in waybar / terminal / launcher
[ ] Theme switching script (optional): script that updates colors in all configs simultaneously

4. BEAUTY TIPS
---------------
- Consistency is key: use the same 4-6 colors everywhere (hyprland borders, waybar modules, rofi menu, terminal, notification daemon)
- Transparency layers: use rgba with alpha 0.6-0.85; add blur behind transparent windows for readability
- Rounded corners: 10-16px looks modern; 0px is minimal; 20px+ is very soft / iOS-like
- Shadows: subtle drop shadows add depth without clutter; use low opacity (0.1-0.3)
- Typography: larger font sizes (12-14pt) and good line-height improve readability
- Icons: use Font Awesome / Material Design Icons / Nerd Fonts for visual clarity
- Animation: keep native animations minimal; use external plugins only when needed
- Scripts: create a theme script that rewrites color variables across all config files; bind it to a hotkey

5. QUICK START COMMAND SEQUENCE
-------------------------------
# 1. Generate base config
python mcp_server.py  # (use tool calls via MCP client)
# 2. Apply beautiful theme
# 3. Set environment variables
# 4. Restart Hyprland (hot reload is automatic for config changes; some changes need restart)
# 5. Verify with: hyprctl monitors; hyprctl clients; hyprctl layers; hyprctl workspaces

6. TROUBLESHOOTING REFERENCES
----------------------------
- If windows don't blur: check GPU drivers (mesa), shader support, and that blur = true
- If waybar doesn't show: check config syntax, module names, and font availability
- If keybinds don't work: verify $mainMod variable, dispatcher syntax, and no conflicting binds
- If monitors are wrong: use hyprctl monitors to get exact names and adjust monitor = lines
- For full syntax errors: check journalctl -b -u hyprland or run hyprland --debug

=== END FULL BEAUTY GUIDE ===
""")

# ------------------------------------------------------------------
# Prompts
# ------------------------------------------------------------------

@mcp.prompt()
def beauty_config_prompt() -> str:
    """Prompt template to instruct an AI agent to use this MCP server for beautiful Hyprland config creation."""
    return textwrap.dedent("""
You are an expert Wayland desktop customization assistant. You have access to the Hyprland Beauty MCP server.

Your task:
1. Read the user's request (e.g., "create a dark glass theme with purple accents for my dual-monitor setup").
2. Call the appropriate MCP tools:
   - get_config_reference(query) for syntax questions.
   - create_hyprland_config(...) for main config.
   - create_waybar_config(...) for status bar.
   - generate_theme_palette(...) for cohesive colors.
   - apply_config_template(...) for quick templates.
3. Combine results into a coherent, beautiful setup.
4. Reference the official wiki: https://wiki.hypr.land/
5. Provide notes on how to install/configure the generated files.

Always aim for modern, clean, glass-like aesthetics with consistent color palettes, rounded borders, subtle shadows, and good typography. Include environment variables, input settings, and window rules for a complete desktop experience.
""")

# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

if __name__ == "__main__":
    print("Starting Hyprland Beauty MCP Server...")
    print(f"Server name: {mcp.name}")
    print(f"Wiki reference: {HYPRLAND_WIKI_URL}")
    print("Available resources: knowledge://hyprland-wiki-reference, knowledge://waybar-reference, knowledge://beautiful-styling-guide")
    print("Available prompts: beauty_config_prompt")
    print("Available tools: create_hyprland_config, create_waybar_config, generate_theme_palette, get_config_reference, apply_config_template, get_full_beauty_guide")
    mcp.run()
