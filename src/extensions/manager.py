# SessionIntent Extensions Manager
# Manages GNOME Shell extensions

"""
SessionIntent Extensions Manager
Handles enabling and disabling GNOME Shell extensions.
"""

from __future__ import annotations

import subprocess
from typing import Any


# Common GNOME extensions with UUID and display name
# Users can reference extensions by name or UUID in config
EXTENSION_REGISTRY: dict[str, str] = {
    # Popular extensions
    "dash to panel": "dash-to-panel@jderose9.github.com",
    "dash to dock": "dash-to-dock@micxgx.gmail.com",
    "workspace indicator": "workspace-indicator@gnome-shell-extensions.gcampax.github.com",
    "top bar organiser": "top-bar-organizer@franglais125.gmail.com",
    "appfolders manager": "appfolders-manager@ddubson.gmail.com",
    "arc menu": "arc-menu@linxgem33.com",
    "bluetooth quick connect": "bluetooth-quick-connect@braams.github.com",
    "caffeine": "caffeine@patapon.info",
    "clipboard indicator": "clipboard-indicator@tudmotu.com",
    "color picker": "color-picker@raultoto.github.com",
    "compiz alike magic lamp": "magic-lamp@",
    "compiz windows effect": "windows-effect@compiz-w effects.github.com",
    "count down": "countdown@maestroschan.fr",
    "coverflow alt tab": "coverflow-alt-tab@eyenx.gmail.com",
    "cpu power manager": "cpupower@maniac-vision.github.com",
    "dash to dock for COS": "dash-to-dock-simply-work@adevait.one",
    "desktop icons ng": "ding@rastersoft.com",
    "diff launcher": "diff-launcher@nls1729.gmail.com",
    "docker integration": "docker-compose@centurylinkcloud.clc.docker",
    "draw on your screen": "draw-on-your-screen@albertomh.com",
    "easy screen cast": "easyscreencast@martin-novak.github.com",
    "emoji picker": "emoji-selector@maestroschan.fr",
    "extension list": "extensions@ulist.dev",
    "extension manager": "ExtensionManager@awake.ebbear.com",
    "forge": "forge@elad.parsons@gmail.com",
    "frame": "frame@axetib.github.com",
    "frippery move clock": "frippery-move-clock@gmail.com",
    "frippery panel favorites": "frippery-panel-favorites@gmail.com",
    "gesture improvements": "gestureImprovements@gestures",
    "gif wallpaper": "gifwallpaper@kaibalba.github.com",
    "gnome global dark theme": "gnome-global-dark-theme@christopher-buss.net",
    "gnome mpv": "gnome-mpv@achadwick.xyz",
    "gnome night light": "night-light-slider@kwolniak.gmail.com",
    "gsconnect": "gsconnect@andyholmes.github.io",
    "hangout indicator": "hangouts-indicator@cloud-9.net",
    "hide top bar": "hide-top-bar@ftsrg.info",
    "impatience": "impatience@gfxmonk.net",
    "installed extension": "installed-extension@masgae.com",
    "k status notifier": "kstatus-notifier-item@andyholmes.github.io",
    "keep awake": "keep-awake@alextruong.dev",
    "lock screen": "lock-screen@christopher-buss.net",
    "logarithm themes": "logarithmshell-themes@grindhold.de",
    "mediacontrols": "mediacontrols@cliffniff.github.com",
    "netspeed": "netspeed@hedidthis.me",
    "notification banner": "notification-banner@braga-live.com.br",
    "open bar": "openbar@victor.campos.gmail.com",
    "open weather": "openweather@jenslody.de",
    "origami": "origami@coopermw.com",
    "pomodoro": "pomodoro@arun.codit",
    "pop shell": "pop-shell@system76.com",
    "power profile": "power-profile-switcher@elias_andersson.dalgren.se",
    "quick settings tweaker": "quick-settings-tweaker@qwreey",
    "removable drive menu": "drive-menu@gnome-shell-extensions.gcampax.github.com",
    "rounded corners": "rounded-corners@fxgn",
    "run by shell": "run-by-shell@b00mer.github.com",
    "screenshot tool": "screenshot-tool@raulf",
    "search light": "search-light@carterb.dev",
    "shortcuts": "shortcuts@glen.stuart@gmail.com",
    "shutter": "shutter@gtema.code",
    "simple dock": "simple-dock@cdch.com",
    "skype status": "skype-status@charles.serrure",
    "smart tap": "smart-tap@kvitzu.gmail.com",
    "sOUND": "s0und@s0und",
    "space bar": "space-bar@luis-pomare",
    "steal my focus": "steal-my-focus@gmail.com",
    "system monitor": "system-monitor@paradoxxx.zero.gmail.com",
    "tactic": "tactic@tool.appwizard",
    "teleport": "teleport@elias_andersson.dalgren.se",
    "tile grid": "tile-grid@alice.lpu",
    "tiling assistant": "tiling-assistant@tonyfu",
    "todotxt": "todotxt@elijahandersen.org",
    "top bar calendar": "top-bar-calendar@",
    "trash": "trash@vesta.computer",
    "ubuntu dock": "ubuntu-dock@ubuntu.com",
    "unite": "unite@hardpixel.eu",
    "user themes": "user-themes@gnome-shell-extensions.gcampax.github.com",
    "vdi connector": "vdi-connector@ubus.it",
    "vertical satellite": "vertical-satellite-ew@TGZ",
    "vitals": "vitals@corecoding.com",
    "volume mixer": "volume-mixer@ponydev.info",
    "waiter": "waiter@lazygeorge.com",
    "weather": "weather@mocturtl.github.com",
    "web search provider": "web-search-provider@eliezer-b",
    "window animator": "window-animator@fxgn",
    "windows navigator": "windows-navigator@Number876",
    "wizard": "wizard@tool.appwizard",
    "x11gestures": "x11gestures@nv7.git",
    "yes panic": "yespanic@sgtdge",
}


def resolve_extension_id(identifier: str) -> str | None:
    """
    Resolve an extension identifier to its UUID.

    Args:
        identifier: Extension name (e.g., "Dash to Panel") or UUID

    Returns:
        UUID if found, None otherwise
    """
    # Check if it's already a UUID (contains @)
    if "@" in identifier:
        return identifier

    # Normalize identifier: replace hyphens with spaces for matching
    identifier_normalized = identifier.lower().replace("-", " ").replace("_", " ")

    # Look up by name (case-insensitive)
    for name, uuid in EXTENSION_REGISTRY.items():
        name_normalized = name.lower().replace("-", " ").replace("_", " ")

        # Exact match
        if name_normalized == identifier_normalized:
            return uuid

        # Partial match: identifier is contained in name or vice versa
        if (
            identifier_normalized in name_normalized
            or name_normalized in identifier_normalized
        ):
            return uuid

    return None


def list_extensions(dev_mode: bool = False) -> list[str]:
    """
    List all installed GNOME Shell extensions.

    Args:
        dev_mode: If True, return empty list

    Returns:
        List of extension UUIDs
    """
    if dev_mode:
        return []

    try:
        result = subprocess.run(
            ["gnome-extensions", "list", "--user"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [line.strip() for line in result.stdout.split("\n") if line.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def get_enabled_extensions(dev_mode: bool = False) -> list[str]:
    """
    Get list of enabled extensions.

    Args:
        dev_mode: If True, return test data

    Returns:
        List of enabled extension UUIDs
    """
    if dev_mode:
        return ["dash-to-panel@jderose9.github.com"]

    try:
        result = subprocess.run(
            ["gnome-extensions", "list", "--user", "--enabled"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [line.strip() for line in result.stdout.split("\n") if line.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def get_extension_info(uuid: str, dev_mode: bool = False) -> dict[str, Any] | None:
    """
    Get information about an extension.

    Args:
        uuid: Extension UUID
        dev_mode: If True, return mock data

    Returns:
        Dict with extension info or None
    """
    if dev_mode:
        return {
            "uuid": uuid,
            "name": "Mock Extension",
            "state": "ENABLED" if uuid in get_enabled_extensions(True) else "DISABLED",
        }

    try:
        result = subprocess.run(
            ["gnome-extensions", "info", uuid],
            capture_output=True,
            text=True,
            check=True,
        )
        info = {}
        for line in result.stdout.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip().lower().replace(" ", "_")] = value.strip()
        return info
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def enable_extension(uuid: str, dev_mode: bool = False) -> tuple[bool, str]:
    """
    Enable a GNOME Shell extension.

    Args:
        uuid: Extension UUID
        dev_mode: If True, print command instead of executing

    Returns:
        Tuple of (success, message)
    """
    if dev_mode:
        return True, f"[DEV] Would enable extension: {uuid}"

    try:
        # First check if extension exists
        info = get_extension_info(uuid)
        if info is None:
            return False, f"Error: Extension '{uuid}' does not exist"

        subprocess.run(
            ["gnome-extensions", "enable", uuid], capture_output=True, check=True
        )
        return True, f"Enabled extension: {uuid}"
    except subprocess.CalledProcessError as e:
        return False, f"Error: Failed to enable '{uuid}': {e.stderr}"
    except FileNotFoundError:
        return False, "Error: gnome-extensions command not found"


def disable_extension(uuid: str, dev_mode: bool = False) -> tuple[bool, str]:
    """
    Disable a GNOME Shell extension.

    Args:
        uuid: Extension UUID
        dev_mode: If True, print command instead of executing

    Returns:
        Tuple of (success, message)
    """
    if dev_mode:
        return True, f"[DEV] Would disable extension: {uuid}"

    try:
        # First check if extension exists
        info = get_extension_info(uuid)
        if info is None:
            return False, f"Error: Extension '{uuid}' does not exist"

        subprocess.run(
            ["gnome-extensions", "disable", uuid], capture_output=True, check=True
        )
        return True, f"Disabled extension: {uuid}"
    except subprocess.CalledProcessError as e:
        return False, f"Error: Failed to disable '{uuid}': {e.stderr}"
    except FileNotFoundError:
        return False, "Error: gnome-extensions command not found"


def apply_extensions(
    extensions_config: dict[str, list[str]], dev_mode: bool = False
) -> list[str]:
    """
    Apply extension configuration for a mode.

    Args:
        extensions_config: Dict with 'enable' and/or 'disable' lists
        dev_mode: If True, print commands instead of executing

    Returns:
        List of status messages
    """
    messages = []

    # Enable extensions
    enable_list = extensions_config.get("enable", [])
    for ext in enable_list:
        uuid = resolve_extension_id(ext)
        if uuid:
            success, msg = enable_extension(uuid, dev_mode)
            messages.append(msg)
        else:
            messages.append(f"Error: Extension '{ext}' not recognized")

    # Disable extensions
    disable_list = extensions_config.get("disable", [])
    for ext in disable_list:
        uuid = resolve_extension_id(ext)
        if uuid:
            success, msg = disable_extension(uuid, dev_mode)
            messages.append(msg)
        else:
            messages.append(f"Error: Extension '{ext}' not recognized")

    return messages


def is_extension_installed(uuid: str, dev_mode: bool = False) -> bool:
    """
    Check if an extension is installed.

    Args:
        uuid: Extension UUID
        dev_mode: If True, return True

    Returns:
        True if installed
    """
    if dev_mode:
        return True

    extensions = list_extensions(dev_mode=False)
    return uuid in extensions
