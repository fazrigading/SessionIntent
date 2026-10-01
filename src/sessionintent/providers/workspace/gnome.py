"""
SessionIntent Workspace Manager
Provides workspace switching via extension socket (GNOME 46+) or gdbus (legacy).
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import time

from .ewmh import EwmhWorkspaceProvider

SOCKET_NAME = "sessionintent-ws.sock"
EXTENSION_UUID = "sessionintent-ws@fazrigading.github.io"
EXTENSION_SOURCE_DIR = "sessionintent-ws"

_WS_SWITCH_TIMEOUT: float = 2.0
_WS_POLL_INTERVAL: float = 0.1


def _get_socket_path(dev_mode: bool = False) -> str:
    if dev_mode:
        return "/dev/null/sessionintent-ws.sock"
    # ponytail: /tmp fallback mirrors extension.js getSocketPath
    runtime_dir = os.environ.get("XDG_RUNTIME_DIR") or "/tmp"
    return f"{runtime_dir}/{SOCKET_NAME}"


def _socket_call(
    cmd: str, timeout: float = 2.0, dev_mode: bool = False
) -> tuple[bool, str]:
    """
    Send a command to the extension socket and return (success, response).

    Args:
        cmd: Command to send (e.g. "SWITCH 1\n" or "CURRENT\n")
        timeout: Socket operation timeout in seconds
        dev_mode: If True, return mock values

    Returns:
        Tuple of (ok, response_text)
    """
    if dev_mode:
        if cmd.startswith("CURRENT"):
            return (True, "0")
        if cmd.startswith("COUNT"):
            return (True, "4")
        if cmd.startswith("SWITCH"):
            return (True, "OK")
        return (True, "OK")

    sock_path = _get_socket_path(dev_mode)
    if not sock_path:
        return (False, "XDG_RUNTIME_DIR not set")
    if not os.path.exists(sock_path):
        return (False, f"Socket not found at {sock_path}")

    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect(sock_path)
        sock.sendall(cmd.encode("utf-8"))
        sock.shutdown(socket.SHUT_WR)
        data = sock.recv(4096)
        sock.close()
        response = data.decode("utf-8").strip()
        return (True, response)
    except socket.timeout:
        return (False, "Socket timeout")
    except OSError as e:
        return (False, f"Socket error: {e}")


def _is_extension_available(dev_mode: bool = False) -> bool:
    ok, _ = _socket_call("CURRENT\n", timeout=0.5, dev_mode=dev_mode)
    return ok


def _gdbus_workspace_call(js_code: str, dev_mode: bool = False) -> tuple[bool, str]:
    """
    Call GNOME Shell via org.gnome.Shell.Eval D-Bus method.

    Args:
        js_code: JavaScript code to evaluate
        dev_mode: If True, return mock values

    Returns:
        Tuple of (ok, stdout_output)
    """
    if dev_mode:
        if "get_active_workspace_index" in js_code:
            return (True, "(uint32 0,)")
        if "_workspaces.length" in js_code or "get_n_workspaces" in js_code:
            return (True, "(uint32 4,)")
        return (True, "(false, '')")
    try:
        result = subprocess.run(
            [
                "gdbus",
                "call",
                "--session",
                "--dest",
                "org.gnome.Shell",
                "--object-path",
                "/org/gnome/Shell",
                "--method",
                "org.gnome.Shell.Eval",
                js_code,
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return (result.returncode == 0, result.stdout.strip())
    except (OSError, subprocess.SubprocessError) as e:
        return (False, str(e))


def switch_workspace(
    workspace_num: int,
    dev_mode: bool = False,
    monitor: str | None = None,
) -> bool:
    """
    Switch to the specified workspace, optionally on a specific monitor.

    Args:
        workspace_num: 1-indexed workspace number
        dev_mode: If True, print commands instead of executing
        monitor: Optional monitor label (e.g. "HDMI-1") to switch on

    Returns:
        True if switch was successful, False otherwise
    """
    if dev_mode:
        monitor_str = f" on monitor {monitor}" if monitor else ""
        print(f"[DEV] Switching to workspace {workspace_num}{monitor_str}")
        return True

    idx = workspace_num - 1  # Convert to 0-indexed

    # Prefer: socket (extension) → gdbus (legacy) → fail with warning
    if _is_extension_available(dev_mode):
        cmd = f"SWITCH {idx}"
        if monitor:
            cmd += f" {monitor}"
        cmd += "\n"
        ok, resp = _socket_call(cmd, dev_mode=dev_mode)
        if ok:
            # ERR from extension is authoritative, don't mask with gdbus retry
            return resp == "OK"

    # gdbus fallback only when socket transport failed (Eval disabled on 46+)
    js = (
        f"global.workspace_manager.get_workspace_by_index({idx})"
        ".activate(global.get_current_time())"
    )
    ok, out = _gdbus_workspace_call(js, dev_mode)
    if ok and "true" in out.lower():
        time.sleep(0.5)
        return True

    return False


def wait_for_workspace(
    target: int,
    dev_mode: bool = False,
    timeout: float = _WS_SWITCH_TIMEOUT,
) -> bool:
    """
    Poll until the active workspace matches the target, or timeout.

    Args:
        target: 1-indexed workspace number to wait for
        dev_mode: If True, return immediately
        timeout: Maximum seconds to wait

    Returns:
        True if workspace matches target, False if timeout
    """
    if dev_mode:
        return True

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        current = get_current_workspace(dev_mode)
        if current == target:
            return True
        time.sleep(_WS_POLL_INTERVAL)

    return False


def get_current_workspace(dev_mode: bool = False) -> int | None:
    """
    Get the current workspace number (1-indexed).

    Args:
        dev_mode: If True, return 1

    Returns:
        1-indexed workspace number, or None if not available
    """
    if dev_mode:
        return 1

    if _is_extension_available(dev_mode):
        ok, resp = _socket_call("CURRENT\n", timeout=1.0, dev_mode=dev_mode)
        if ok:
            try:
                return int(resp) + 1  # Convert to 1-indexed
            except ValueError:
                pass

    ok, output = _gdbus_workspace_call(
        "global.workspace_manager.get_active_workspace_index()"
    )
    if ok:
        import re

        match = re.search(r"uint32\s+(\d+)", output)
        if match:
            return int(match.group(1)) + 1  # Convert to 1-indexed

    return None


def get_workspace_count(dev_mode: bool = False) -> int:
    """
    Get the total number of workspaces.

    Args:
        dev_mode: If True, return 1

    Returns:
        Number of workspaces
    """
    if dev_mode:
        return 1

    if _is_extension_available(dev_mode):
        ok, resp = _socket_call("COUNT\n", timeout=1.0, dev_mode=dev_mode)
        if ok:
            try:
                return int(resp)
            except ValueError:
                pass

    ok, output = _gdbus_workspace_call(
        "global.workspace_manager.get_n_workspaces()"
    )
    if ok:
        import re

        match = re.search(r"uint32\s+(\d+)", output)
        if match:
            return int(match.group(1))

    return 1


def _is_extension_enabled(dev_mode: bool = False) -> bool:
    if dev_mode:
        return True
    try:
        result = subprocess.run(
            ["gnome-extensions", "list", "--enabled"],
            capture_output=True,
            text=True,
            check=True,
        )
        return EXTENSION_UUID in result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _enable_extension(dev_mode: bool = False) -> tuple[bool, str]:
    if dev_mode:
        return (True, "[DEV] Would enable extension")
    try:
        subprocess.run(
            ["gnome-extensions", "enable", EXTENSION_UUID],
            capture_output=True,
            text=True,
            check=True,
        )
        return (True, "Extension enabled")
    except subprocess.CalledProcessError as e:
        return (False, f"Failed to enable extension: {e.stderr.strip()}")
    except FileNotFoundError:
        return (False, "gnome-extensions command not found")


def _extension_needs_update(ext_dir: str, source_dir: str) -> bool:
    """True if installed metadata differs from source (version/shell-version)."""
    try:
        with open(os.path.join(ext_dir, "metadata.json")) as f:
            installed = json.load(f)
        with open(os.path.join(source_dir, "metadata.json")) as f:
            source = json.load(f)
    except (OSError, ValueError):
        return False
    return installed.get("version") != source.get("version") or installed.get(
        "shell-version"
    ) != source.get("shell-version")


def ensure_extension(dev_mode: bool = False) -> tuple[bool, str]:
    """
    Ensure the SessionIntent workspace-switcher extension is installed and enabled.

    Args:
        dev_mode: If True, return success without installing

    Returns:
        Tuple of (installed_and_enabled, message)
    """
    if dev_mode:
        return (True, "[DEV] Would ensure extension is installed")

    ext_dir = os.path.join(
        os.path.expanduser("~/.local/share/gnome-shell/extensions"),
        EXTENSION_UUID,
    )
    source_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "extensions",
        EXTENSION_SOURCE_DIR,
    )

    if not os.path.exists(ext_dir):
        if not os.path.exists(source_dir):
            return (
                False,
                f"Extension source not found at {source_dir}",
            )
        try:
            import shutil

            shutil.copytree(source_dir, ext_dir)
        except OSError as e:
            return (False, f"Failed to copy extension: {e}")
        updated = True
    elif _extension_needs_update(ext_dir, source_dir):
        try:
            import shutil

            shutil.rmtree(ext_dir)
            shutil.copytree(source_dir, ext_dir)
        except OSError as e:
            return (False, f"Failed to update extension: {e}")
        updated = True
    else:
        updated = False

    if _is_extension_enabled(dev_mode):
        if updated:
            return (
                True,
                f"Extension updated at {ext_dir}. "
                "Restart GNOME Shell (Alt+F2 → r) to activate.",
            )
        return (True, f"Extension already enabled at {ext_dir}")

    ok, msg = _enable_extension(dev_mode)
    if not ok:
        return (
            False,
            f"{msg}. Run manually: gnome-extensions enable {EXTENSION_UUID}",
        )

    return (
        True,
        f"Extension installed and enabled at {ext_dir}. "
        "Restart GNOME Shell (Alt+F2 → r) to activate.",
    )


class GnomeWorkspaceProvider:
    """GNOME workspace management via extension socket with gdbus fallback."""

    def __init__(self, dev_mode: bool = False) -> None:
        self._dev_mode = dev_mode
        self._ewmh = EwmhWorkspaceProvider(dev_mode=dev_mode)

    def switch_workspace(
        self,
        num: int,
        monitor: str | None = None,
    ) -> bool:
        return switch_workspace(num, self._dev_mode, monitor=monitor)

    def get_current_workspace(self) -> int | None:
        return get_current_workspace(self._dev_mode)

    def get_workspace_count(self) -> int:
        return get_workspace_count(self._dev_mode)

    def wait_for_workspace(self, target: int, timeout: float = 2.0) -> bool:
        return wait_for_workspace(target, self._dev_mode, timeout=timeout)

    def wait_for_window(
        self,
        app_pattern: str,
        target_workspace: int,
        timeout: float = 15.0,
    ) -> bool:
        # xdotool-based wait is desktop-agnostic; shared with the EWMH provider.
        return self._ewmh.wait_for_window(app_pattern, target_workspace, timeout)


__all__ = [
    "switch_workspace",
    "get_current_workspace",
    "get_workspace_count",
    "wait_for_workspace",
    "ensure_extension",
    "GnomeWorkspaceProvider",
]