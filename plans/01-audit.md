# 01 — Current-State Audit

This document records the state of SessionIntent as it actually exists in the codebase.
It is deliberately grounded in the source files, not in `PROJECT_SUMMARY.md` or
`SUGGESTIONS.md`, both of which overstate what is implemented.

## 1. Architecture actually present

The package root is `src/`. The import style is `src.session`, `src.cli`,
`src.constants`, and so on, not a nested `src/sessionintent/` namespace. The `pyproject.toml`
entry point maps the command to the module directly:

```toml
[project.scripts]
sessionintent = "src.__main__:main"
```

This is an unusual package name (`src`), and it is the source of most of the packaging
and CI breakage documented below.

### Real module inventory

The following directories exist under `src/` and contain real code:

| Directory | Files present |
|-----------|---------------|
| `src/app/` | `__init__.py`, `app_categories.yaml`, `cache.py`, `controller.py`, `detect.py`, `registry.py`, `setup.py`, `template.py` |
| `src/cli/` | `__init__.py`, `parser.py` |
| `src/config/` | `__init__.py`, `loader.py`, `validator.py`, `watcher.py` |
| `src/constants/` | `__init__.py`, `defaults.py`, `paths.py` |
| `src/extensions/` | `__init__.py`, `manager.py` |
| `src/hardware/` | `__init__.py`, `power.py` |
| `src/plugins/` | `__init__.py`, `system.py` |
| `src/session/` | `__init__.py`, `log.py`, `manager.py`, `notify.py`, `scheduler.py`, `snapshot.py`, `state.py` |
| `src/ui/` | `__init__.py`, `display.py`, `selector.py`, `theme.py` |
| `src/workspace/` | `__init__.py`, `manager.py` |

`PROJECT_SUMMARY.md` lists a similar tree, but describes several of these modules as
fully implemented features when in practice they are unwired or broken (see sections 2
and 3 below).

## 2. Concrete bugs

| # | Bug | Location | Impact |
|---|-----|----------|--------|
| 1 | `--version` flag is declared but never handled; invoking it returns exit code 0 with no output. | `src/cli/parser.py:148` declares the flag; `src/__main__.py` has no branch for it. | Broken command; the version cannot be printed. |
| 2 | `--force` is validated but never passed into setup/scan. `--no-cache` is used, but `--force` is silently ignored. | `src/__main__.py:74-78` and `src/__main__.py:57-72`. | Dead flag; users cannot force a fresh scan. |
| 3 | `snapshot.py` shells out to `wmctl`, a typo for `wmctrl`. | `src/session/snapshot.py:69` and `src/session/snapshot.py:152`. | Snapshot listing and restore are silently broken. |
| 4 | Version numbers disagree across files. | `pyproject.toml` says `0.3.1`; `src/__init__.py` says `0.3.3`; `packaging/fedora/sessionintent.spec` says `0.2.0`; `man/sessionintent.1` says `0.3.3`. | Confusing releases; the "single source of truth" is missing. |
| 5 | `resolve_template` is duplicated with divergent behavior. | `src/app/controller.py:209` vs `src/app/template.py:12`. | The controller's private version is used at launch time, while the exported `template.resolve_template` is not; two implementations can drift. |
| 6 | `load_apps()` (used) duplicates `AppRegistry` (unused). | `src/config/loader.py:50` vs `src/app/registry.py:14`. | Two sources of truth for the app registry. |
| 7 | `INSTALL.sh` copies a nonexistent `sessionintent.py`. | `INSTALL.sh:99`. | The installer cannot actually install the package. |
| 8 | RPM spec references `sessionintent.py` and has a `%{_ datadir}` typo. | `packaging/fedora/sessionintent.spec:42` and `:49`. | The spec is broken. |
| 9 | `ci.yml` references `sessionintent.py` and `requirements.txt`, neither of which exists. | `.github/workflows/ci.yml:27-31`. | CI is broken out of the box. |
| 10 | Dev-mode socket path inconsistency: `get_current_workspace` and `switch_workspace` call `_is_extension_available(dev_mode)`, but the `_socket_call` they invoke does not receive `dev_mode`; `_socket_call` then calls `_get_socket_path(dev_mode=False)` even when dev mode is on. | `src/workspace/manager.py`. | Latent dev-mode behavior mismatch. |

## 3. Dead / unwired code

These modules are defined but never reachable from the main execution flow:

| Module | Evidence of being unwired |
|--------|---------------------------|
| `src/session/scheduler.py` (`TimeScheduler`) | Not instantiated or started anywhere in `__main__.py` or `SessionManager`. |
| `src/session/notify.py` | No caller in `SessionManager` or the CLI. |
| `src/ui/theme.py` | Theme system is never applied to the selector. |
| `src/plugins/system.py` (`PluginManager`) | `get_plugin_manager` is exported but never invoked. |
| `src/config/watcher.py` | The watcher is never started; only the manual `--reload` command exists. |
| `src/app/registry.py` (`AppRegistry`) | Superseded by `config.load_apps()`. |
| `launch_apps_async` in `src/app/controller.py` | `apply_mode` uses the synchronous `launch_app`, not the async variant. |

The principle in `02-vision.md` is that every module must be **wired or removed**. These
modules are the initial candidates for deletion (or, where a feature is genuinely wanted,
explicit wiring in a later phase).

## 4. Doc / claim drift

- `PROJECT_SUMMARY.md` labels the project "production-ready" and lists "259 tests",
  "async app launching", "config hot reload", "plugin system", "scheduler", and
  "notifications". Several of these are unwired or broken (sections 2 and 3). The
  "async app launching" claim is misleading because the sync path is what actually runs.
- `docs/ARCHITECTURE.md` contains duplicated component blocks (Hardware Detector, Mode
  Selector, Workspace Manager, App Controller each appear twice in the diagram).
- `docs/INSTALLATION.md` references `sessionintent.py`, `config.yaml.example`, and
  `apps.yaml.example` at the repo root; those example files live under `examples/`.
- `LINUX_DESKTOP_COMPATIBILITY_PLAN.md` and `TODO.md` describe multi-desktop provider
  work that does not exist in the code. None of the provider/detector modules are present.
- Empty directories imply planned work that was never completed: `packaging/Arch/` and
  `scripts/`.

## 5. Summary of the problem

SessionIntent has a working GNOME/Wayland core (`apply_mode`, state management, app
launch/reuse, the GNOME workspace extension), but it is wrapped in documentation and
tooling that describe a more mature product than the code delivers. The rework must
first make the code, tests, CI, and docs agree with each other, and only then add new
capability.

See `04-phases.md` for how the findings here translate into ordered work.
