"""
SessionIntent Setup
Interactive setup wizard for first-run and app scanning.
"""

from __future__ import annotations

from typing import Any

from ..app.detect import (
    detect_all_apps,
    get_category_list,
    get_categorized_apps,
)
from ..constants import APPS_PATH, CONFIG_DIR, CONFIG_PATH, DEFAULT_CONFIG
from ..session.log import info


CATEGORY_HEADER = {
    "Browsers": "# Browsers",
    "Development": "# Development",
    "Media Players": "# Media Players",
    "Art Editing": "# Art Editing",
    "Communication": "# Communication",
    "Games": "# Games",
    "Productivity": "# Productivity",
    "Utilities": "# Utilities",
    "System": "# System",
    "Other": "# Other",
}


def prompt_yes_no(prompt_text: str) -> bool:
    """Prompt user for yes/no input."""
    while True:
        try:
            response = input(f"{prompt_text} [Y/n]: ").strip().lower()
            if response in ("y", "yes", ""):
                return True
            if response in ("n", "no"):
                return False
        except (KeyboardInterrupt, EOFError):
            return False


def prompt_numbered_list(prompt_text: str, items: list[str]) -> list[int]:
    """Prompt user to select numbered items."""
    while True:
        try:
            print(prompt_text)
            response = input("Enter numbers (comma-separated): ").strip()
            if not response:
                return []

            selected = []
            for part in response.split(","):
                part = part.strip()
                if not part.isdigit():
                    continue
                num = int(part)
                if 1 <= num <= len(items):
                    selected.append(num)

            return selected
        except (KeyboardInterrupt, EOFError):
            return []


def parse_selection(selection_str: str, max_num: int) -> list[int]:
    """Parse comma-separated selection string."""
    selected = []
    for part in selection_str.split(","):
        part = part.strip()
        if not part.isdigit():
            continue
        num = int(part)
        if 1 <= num <= max_num:
            selected.append(num)
    return selected


def select_categories(categorized: dict[str, dict[str, dict[str, Any]]]) -> list[str]:
    """Prompt user to select categories."""
    categories = get_category_list()
    print("\nSelect categories to include:")
    for cat, num in categories:
        count = len(categorized.get(cat, {}))
        print(f"  {num}. {cat} ({count} apps)")
    all_count = sum(len(apps) for apps in categorized.values())
    print(f"  11. All categories ({all_count} apps)")

    while True:
        try:
            response = input("\nEnter numbers (comma-separated): ").strip()
            if not response:
                return []

            numbers = parse_selection(response, 11)
            if 11 in numbers:
                return [cat for cat, _ in categories]
            if 11 not in numbers and numbers:
                selected = []
                for num in numbers:
                    if 1 <= num <= 10:
                        selected.append(categories[num - 1][0])
                return selected
        except (KeyboardInterrupt, EOFError):
            return []


def select_apps_option() -> int:
    """Prompt user to select app inclusion option."""
    print("\nSelect apps to include:")
    print("  1. Exclude few apps (include all, then exclude selected)")
    print("  2. Include few apps (start fresh, include only selected)")
    print("  3. Use all apps")

    while True:
        try:
            response = input("\nEnter number: ").strip()
            if response.isdigit() and 1 <= int(response) <= 3:
                return int(response)
        except (KeyboardInterrupt, EOFError):
            return 3


def select_apps_to_exclude(categorized_apps: dict[str, dict[str, Any]]) -> set[str]:
    """Prompt user to select apps to exclude."""
    excluded: set[str] = set()

    for category, apps in categorized_apps.items():
        print(f"\n{category}:")
        app_list = list(apps.keys())
        for i, app_key in enumerate(app_list, 1):
            print(f"  {i}. {app_key}")

        if not app_list:
            continue

        try:
            response = input(
                "Enter numbers to EXCLUDE (comma-separated, or press Enter to skip): "
            ).strip()
            if not response:
                continue

            numbers = parse_selection(response, len(app_list))
            for num in numbers:
                excluded.add(app_list[num - 1])
        except (KeyboardInterrupt, EOFError):
            pass

    return excluded


def select_apps_to_include(categorized_apps: dict[str, dict[str, Any]]) -> set[str]:
    """Prompt user to select apps to include."""
    included: set[str] = set()

    for category, apps in categorized_apps.items():
        print(f"\n{category}:")
        app_list = list(apps.keys())
        for i, app_key in enumerate(app_list, 1):
            print(f"  {i}. {app_key}")

        if not app_list:
            continue

        try:
            response = input(
                "Enter numbers to INCLUDE (comma-separated, or press Enter for all): "
            ).strip()
            if not response:
                included.update(app_list)
                continue

            numbers = parse_selection(response, len(app_list))
            for num in numbers:
                included.add(app_list[num - 1])
        except (KeyboardInterrupt, EOFError):
            pass

    return included


def _find_category(app_key: str, categories: list[str]) -> str:
    """First category whose keyword matches app_key, else Other."""
    from ..app.detect import APP_CATEGORIES

    app_key_lower = app_key.lower()
    for cat in categories:
        for kw in APP_CATEGORIES.get(cat, []):
            if kw.lower() in app_key_lower:
                return cat
    return "Other"


def _entry_lines(app_key: str, app_data: dict[str, Any]) -> list[str]:
    """Render one apps.yaml entry (with trailing blank line)."""
    lines = [f"{app_key}:"]
    if cmd := app_data.get("cmd"):
        lines.append(f"  cmd: {cmd}")
    if check := app_data.get("check"):
        if check is False:
            lines.append("  check: false")
        else:
            lines.append(f"  check: {check!r}")
    if internal := app_data.get("internal_reuse"):
        lines.append(f"  internal_reuse: {internal}")
    lines.append("")
    return lines


def build_apps_yaml(
    apps: dict[str, dict[str, Any]],
    selected_categories: list[str],
) -> str:
    """Build YAML content for apps.yaml."""
    categorized: dict[str, dict[str, dict[str, Any]]] = {}

    for app_key in apps:
        found_category = _find_category(app_key, selected_categories)
        if found_category not in categorized:
            categorized[found_category] = {}
        categorized[found_category][app_key] = apps[app_key]

    lines = [
        "# SessionIntent Apps Configuration",
        "#",
        "# Customize launch parameters:",
        "#   - {profile|default} → Firefox profile name",
        "#   - {workspace|} → VSCode workspace path",
        "#   - append_param for URLs to open",
        "#   - primary_param for workspace/project path",
        "#   - flags for CLI options (background, etc.)",
        "#",
        "# Reference: https://github.com/fazrigading/sessionintent",
        "#",
        "",
    ]

    for category in selected_categories:
        if category in CATEGORY_HEADER:
            lines.append(CATEGORY_HEADER[category])

        if category in categorized:
            for app_key in sorted(categorized[category]):
                lines.extend(
                    _entry_lines(app_key, categorized[category][app_key])
                )

    return "\n".join(lines)


def write_apps_yaml(content: str) -> None:
    """Write apps.yaml to user config directory."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(APPS_PATH, "w") as f:
        f.write(content)
    info(f"Apps configuration written to {APPS_PATH}")


def write_config_yaml() -> None:
    """Write default config.yaml to user config directory."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        f.write(DEFAULT_CONFIG)
    info(f"Default config written to {CONFIG_PATH}")


def _load_existing_app_keys() -> set[str]:
    """App keys already configured in apps.yaml (empty when file is missing)."""
    import yaml

    if not APPS_PATH.exists():
        return set()
    try:
        data = yaml.safe_load(APPS_PATH.read_text()) or {}
    except (OSError, yaml.YAMLError):
        return set()
    return {k for k, v in data.items() if isinstance(v, dict)}


def append_new_apps(
    new_apps: dict[str, dict[str, Any]], categories: list[str]
) -> int:
    """
    Append entries to apps.yaml under matching category headers.

    Args:
        new_apps: Entries keyed by app key
        categories: Category order used for header matching

    Returns:
        Number of entries appended (0 when the file is missing/unwritable)
    """
    try:
        lines = APPS_PATH.read_text().split("\n")
    except OSError:
        return 0

    grouped: dict[str, list[str]] = {}
    for app_key in sorted(new_apps):
        cat = _find_category(app_key, categories)
        grouped.setdefault(cat, []).extend(_entry_lines(app_key, new_apps[app_key]))

    headers = set(CATEGORY_HEADER.values())
    for cat, entry_lines in grouped.items():
        header = CATEGORY_HEADER.get(cat, f"# {cat}")
        if header in lines:
            idx = lines.index(header)
        else:
            lines += ["", header]
            idx = len(lines) - 1
        pos = len(lines)
        for j in range(idx + 1, len(lines)):
            if lines[j] in headers:
                pos = j
                break
        lines[pos:pos] = entry_lines

    try:
        APPS_PATH.write_text("\n".join(lines))
    except OSError:
        return 0
    return len(new_apps)


def setup_interactive(add_new_only: bool = False, use_cache: bool = True) -> None:
    """
    Run interactive setup wizard.

    Args:
        add_new_only: If True, only add new detected apps.
        use_cache: If True, use cached detection results. Defaults to True.
    """
    if not CONFIG_PATH.exists():
        write_config_yaml()

    print("Scanning for installed applications...")

    detected = detect_all_apps(use_cache=use_cache)
    if not detected:
        print("No applications detected on this system.")
        use_example = prompt_yes_no(
            "Would you like to use example apps from GitHub repo"
        )
        if use_example:
            print(
                "Run: curl -o ~/.config/sessionintent/apps.yaml "
                "https://raw.githubusercontent.com/fazrigading/sessionintent/"
                "main/examples/apps.example.yaml"
            )
        return

    if add_new_only and APPS_PATH.exists():
        _add_new_only(detected)
        return

    categories = get_category_list()
    print(f"\nFound {len(detected)} applications in {len(categories) + 1} categories.")

    categorized = get_categorized_apps(detected)
    selected_categories = select_categories(categorized)
    if not selected_categories:
        print("No categories selected. Aborting.")
        return

    filtered = {
        cat: apps
        for cat, apps in categorized.items()
        if cat in selected_categories
    }
    
    option = select_apps_option()

    final_apps: dict[str, dict[str, Any]] = {}

    if option == 1:
        all_flat = {}
        for cat_apps in filtered.values():
            all_flat.update(cat_apps)
        excluded = select_apps_to_exclude(filtered)
        final_apps = {k: v for k, v in all_flat.items() if k not in excluded}
    elif option == 2:
        included = select_apps_to_include(filtered)
        for cat_apps in filtered.values():
            for app_key, app_data in cat_apps.items():
                if app_key in included:
                    final_apps[app_key] = app_data
    else:
        for cat_apps in filtered.values():
            final_apps.update(cat_apps)

    if not final_apps:
        print("No apps selected. Aborting.")
        return

    yaml_content = build_apps_yaml(final_apps, selected_categories)
    write_apps_yaml(yaml_content)

    print(f"\nSetup complete! {len(final_apps)} apps configured.")


def _add_new_only(detected: dict[str, dict[str, Any]]) -> None:
    """Prompt over apps missing from apps.yaml and append the chosen ones."""
    fresh = {
        k: v for k, v in detected.items() if k not in _load_existing_app_keys()
    }
    if not fresh:
        print("No new applications found.")
        return

    keys = sorted(fresh)
    print(f"\n{len(keys)} new applications found:")
    for i, app_key in enumerate(keys, 1):
        print(f"  {i}. {app_key}")

    if prompt_yes_no(f"Add all {len(keys)} new apps?"):
        chosen = keys
    else:
        chosen = [keys[n - 1] for n in prompt_numbered_list("Add which?", keys)]
    if not chosen:
        print("Nothing added.")
        return

    categories = [cat for cat, _ in get_category_list()]
    added = append_new_apps({k: fresh[k] for k in chosen}, categories)
    print(f"\nAdded {added} apps to {APPS_PATH}.")


def rescan_options(use_cache: bool = True) -> None:
    """
    Offer rescan options and run selected.

    Args:
        use_cache: If True, use cached detection results. Defaults to True.
    """
    print("\nRescan options:")
    print("  1. Rescan all apps (re-do entire selection)")
    print("  2. Add only new detected apps")

    while True:
        try:
            response = input("\nEnter number: ").strip()
            if response.isdigit() and 1 <= int(response) <= 2:
                option = int(response)
                break
        except (KeyboardInterrupt, EOFError):
            return

    if option == 1:
        setup_interactive(add_new_only=False, use_cache=use_cache)
    else:
        setup_interactive(add_new_only=True, use_cache=use_cache)