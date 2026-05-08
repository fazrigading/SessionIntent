"""
SessionIntent Workspace Manager
Provides workspace switching via extension socket (GNOME 46+) or gdbus (legacy).
"""

from __future__ import annotations

import os
import socket
import subprocess
import time

SOCKET_NAME = "sessionintent-ws.sock"
EXTENSION_UUID = "sessionintent-ws@fazrigading.github.io"
EXTENSION_SOURCE_DIR = "sessionintent-ws"

_WS_SWITCH_TIMEOUT: float = 2.0
_WS_POLL_INTERVAL: float = 0.1


def _get_socket_path(dev_mode: bool = False) -> str | None:
    if dev_mode:
        return "/dev/null/sessionintent-ws.sock"
    runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
    if not runtime_dir:
        return None
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
        if "_workspaces.length" in js_code:
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
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
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
        ok, resp = _socket_call(cmd)
        if ok and resp == "OK":
            return True

    # gdbus fallback when socket unavailable or when socket call fails
    js = f"Main.wm.actionSwitchWorkspace(Main.wm.get_workspace_by_index({idx}))"
    ok, _ = _gdbus_workspace_call(js, dev_mode)
    if ok:
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
        ok, resp = _socket_call("CURRENT\n", timeout=1.0)
        if ok:
            try:
                return int(resp) + 1  # Convert to 1-indexed
            except ValueError:
                pass

    ok, output = _gdbus_workspace_call("Main.wm.get_active_workspace_index()")
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
        ok, resp = _socket_call("COUNT\n", timeout=1.0)
        if ok:
            try:
                return int(resp)
            except ValueError:
                pass

    ok, output = _gdbus_workspace_call("Main.wm._workspaces.length")
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

    if _is_extension_enabled(dev_mode):
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


_WAIT_WINDOW_POLL_INTERVAL: float = 0.5


def wait_for_window(
    app_pattern: str,
    target_workspace: int,
    timeout: float = 15.0,
    dev_mode: bool = False,
) -> bool:
    """
    Wait for an app window to appear on the target workspace.

    Args:
        app_pattern: Window class pattern to search for (passed to xdotool)
        target_workspace: 1-indexed workspace number to wait for
        timeout: Maximum seconds to wait (default 15s)
        dev_mode: If True, return True immediately

    Returns:
        True if window found on target workspace, False if timeout
    """
    if dev_mode:
        return True

    target_idx = target_workspace - 1
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            result = subprocess.run(
                ["xdotool", "search", "--class", app_pattern],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                window_ids = result.stdout.strip().split("\n")
                for wid in window_ids:
                    if not wid:
                        continue
                    try:
                        desk_result = subprocess.run(
                            ["xdotool", "getwindowenv", wid, "_NET_WM_DESKTOP"],
                            capture_output=True,
                            text=True,
                            timeout=1,
                        )
                        if desk_result.returncode == 0:
                            try:
                                ws_index = int(desk_result.stdout.strip())
                                if ws_index == target_idx:
                                    return True
                            except ValueError:
                                pass
                    except subprocess.TimeoutExpired:
                        pass
        except FileNotFoundError:
            return False
        except (subprocess.SubprocessError, OSError):
            pass

        time.sleep(_WAIT_WINDOW_POLL_INTERVAL)

    return False