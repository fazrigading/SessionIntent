/* SessionIntent Workspace Switcher - GNOME Shell Extension */
/* Modern ESM Architecture for GNOME 45+ */

import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
const SOCKET_NAME = 'sessionintent-ws.sock';

export default class SessionIntentWorkspaceSwitcher extends Extension {
    constructor(metadata) {
        super(metadata);
        this._socketService = null;
        this._socketPath = null;
    }

    getSocketPath() {
        const runtimeDir = GLib.getenv('XDG_RUNTIME_DIR');
        return runtimeDir ? `${runtimeDir}/${SOCKET_NAME}` : `/tmp/${SOCKET_NAME}`;
    }

    findMonitorIndexByLabel(label) {
        const monitors = global.display.get_monitors();
        for (let i = 0; i < monitors.length; i++) {
            const mon = monitors.get_item(i);
            if (mon.get_connector() === label || mon.get_display_name() === label) {
                return i;
            }
        }
        return -1;
    }

    getCurrentWorkspaceIndex() {
        return global.workspace_manager.get_active_workspace_index();
    }

    switchWorkspace(idx, monitorLabel = null) {
        const wsManager = global.workspace_manager;
        if (idx < 0 || idx >= wsManager.get_n_workspaces()) {
            return `ERR: workspace index ${idx} out of range (have ${wsManager.get_n_workspaces()})`;
        }

        const workspace = wsManager.get_workspace_by_index(idx);

        if (monitorLabel !== null) {
            const monIdx = this.findMonitorIndexByLabel(monitorLabel);
            if (monIdx === -1) {
                return `ERR: monitor '${monitorLabel}' not found`;
            }
            workspace.activate_with_focus(global.display.focus_window, monIdx);
        } else {
            // Use Main.wm action if available for proper animation, otherwise direct API
            if (Main.wm && typeof Main.wm.actionSwitchWorkspace === 'function') {
                Main.wm.actionSwitchWorkspace(workspace, global.get_current_time());
            } else if (Main.wm && typeof Main.wm.actionMoveWorkspace === 'function') {
                // Fallback to actionMoveWorkspace
                Main.wm.actionMoveWorkspace(workspace, global.get_current_time());
            } else {
                // Direct API fallback
                workspace.activate(global.get_current_time());
            }
        }

        return "OK";
    }

    handleLine(line) {
        line = line.trim();
        if (!line) {
            return null;
        }

        const parts = line.split(/\s+/);
        const cmd = parts[0];

        switch (cmd) {
            case "SWITCH": {
                if (parts.length < 2) {
                    return "ERR: SWITCH requires workspace index";
                }
                const idx = parseInt(parts[1], 10);
                if (isNaN(idx)) {
                    return "ERR: invalid workspace index";
                }
                const monitorLabel = parts.length > 2 ? parts[2] : null;
                return this.switchWorkspace(idx, monitorLabel);
            }
            case "CURRENT": {
                return String(this.getCurrentWorkspaceIndex());
            }
            case "COUNT": {
                return String(global.workspace_manager.get_n_workspaces());
            }
            case "QUIT": {
                return "BYE";
            }
            default:
                return `ERR: unknown command '${cmd}'`;
        }
    }

    onIncomingConnection(service, connection) {
        new ConnectionHandler(connection, this);
    }

    enable() {
        this._socketPath = this.getSocketPath();

        // Clean up existing socket file
        if (GLib.file_test(this._socketPath, GLib.FileTest.EXISTS)) {
            try {
                Gio.File.new_for_path(this._socketPath).delete(null);
            } catch (e) {
                // Ignore
            }
        }

        // Create Unix socket address
        const address = Gio.UnixSocketAddress.new(this._socketPath);

        // Create SocketService for event-driven async handling
        this._socketService = new Gio.SocketService();

        // Bind to address - add_address returns boolean success
        const result = this._socketService.add_address(
            address,
            Gio.SocketType.STREAM,
            Gio.SocketProtocol.DEFAULT,
            null
        );

        if (!result) {
            log(`[${this.uuid}] Failed to bind socket at ${this._socketPath}`);
            this._socketService = null;
            return;
        }

        // Set socket permissions
        try {
            Gio.File.new_for_path(this._socketPath).set_attribute_string(
                "unix:mode",
                "0600",
                Gio.FileQueryInfoFlags.NONE,
                null
            );
        } catch (e) {
            // Continue even if chmod fails
        }

        // Connect the 'incoming' signal for async event-driven connections
        this._socketService.connect("incoming", this.onIncomingConnection.bind(this));

        // Start listening - use start() method, not set_active()
        this._socketService.start();

        log(`[${this.uuid}] Socket service listening on ${this._socketPath}`);
    }

    disable() {
        if (this._socketService !== null) {
            try {
                this._socketService.stop();
                this._socketService.close(null);
            } catch (e) {
                // Ignore
            }
            this._socketService = null;
        }

        if (this._socketPath !== null) {
            try {
                Gio.File.new_for_path(this._socketPath).delete(null);
            } catch (e) {
                // Ignore
            }
            this._socketPath = null;
        }

        log(`[${this.uuid}] Socket service stopped`);
    }
}

class ConnectionHandler {
    constructor(connection, extension) {
        this._connection = connection;
        this._extension = extension;
        this._buffer = "";
        this._closed = false;
        this._setupStreams();
    }

    _setupStreams() {
        this._inputStream = this._connection.get_input_stream();
        this._outputStream = this._connection.get_output_stream();
        this._scheduleRead();
    }

    _scheduleRead() {
        if (this._closed) return;

        this._inputStream.read_bytes_async(
            256,
            GLib.PRIORITY_DEFAULT,
            null,
            (stream, result) => {
                try {
                    const bytes = stream.read_bytes_finish(result);
                    if (bytes.get_size() === 0) {
                        this._close();
                        return;
                    }
                    const chunk = new TextDecoder().decode(bytes.get_data());
                    this._buffer += chunk;
                    this._processBuffer();
                } catch (e) {
                    this._close();
                }
            }
        );
    }

    _processBuffer() {
        if (this._closed) return;

        let newline;
        while ((newline = this._buffer.indexOf("\n")) !== -1) {
            const line = this._buffer.slice(0, newline);
            this._buffer = this._buffer.slice(newline + 1);

            const response = this._extension.handleLine(line);
            if (response !== null) {
                this._writeResponse(response);
            }
        }

        if (!this._closed) {
            this._scheduleRead();
        }
    }

    _writeResponse(response) {
        if (this._closed) return;

        try {
            const data = new TextEncoder().encode(response + "\n");
            this._outputStream.write_all(
                data,
                data.length,
                null
            );
        } catch (e) {
            this._close();
        }
    }

    _close() {
        if (this._closed) return;
        this._closed = true;
        try {
            this._connection.close(null);
        } catch (e) {
            // Ignore close errors
        }
    }
}