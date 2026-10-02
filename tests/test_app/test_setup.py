"""
Tests for SessionIntent app detection and setup.
"""

from unittest.mock import patch

from sessionintent.app.detect import (
    _parse_desktop_entry,
    _split_exec,
    categorize_app,
    detect_all_apps,
    detect_desktop_apps,
    detect_local_bin_apps,
    get_category_list,
    get_categorized_apps,
)
from sessionintent.app.setup import (
    _add_new_only,
    _load_existing_app_keys,
    append_new_apps,
    parse_selection,
    prompt_yes_no,
    select_apps_option,
)


class TestCategorizeApp:
    """Test app categorization."""

    def test_categorize_firefox(self):
        assert categorize_app("firefox") == "Browsers"

    def test_categorize_chrome(self):
        assert categorize_app("chrome") == "Browsers"

    def test_categorize_chromium(self):
        assert categorize_app("chromium") == "Browsers"

    def test_categorize_vscode(self):
        assert categorize_app("vscode") == "Development"

    def test_categorize_code(self):
        assert categorize_app("code") == "Development"

    def test_categorize_discord(self):
        assert categorize_app("discord") == "Communication"

    def test_categorize_spotify(self):
        assert categorize_app("spotify") == "Media Players"

    def test_categorize_steam(self):
        assert categorize_app("steam") == "Games"

    def test_categorize_lutris(self):
        assert categorize_app("lutris") == "Games"

    def test_categorize_nautilus(self):
        assert categorize_app("nautilus") == "Utilities"

    def test_categorize_gnome_terminal(self):
        assert categorize_app("gnome-terminal") == "System"

    def test_categorize_unknown(self):
        assert categorize_app("unknown-app-123") == "Other"


class TestGetCategoryList:
    """Test get_category_list function."""

    def test_returns_ten_categories(self):
        categories = get_category_list()
        assert len(categories) == 10

    def test_first_category_is_browsers(self):
        categories = get_category_list()
        assert categories[0] == ("Browsers", 1)

    def test_categories_have_numbers(self):
        categories = get_category_list()
        for cat, num in categories:
            assert isinstance(cat, str)
            assert isinstance(num, int)
            assert 1 <= num <= 10

    def test_last_category_is_other(self):
        categories = get_category_list()
        assert categories[-1] == ("Other", 10)


class TestParseSelection:
    """Test parse_selection function."""

    def test_single_number(self):
        result = parse_selection("1", 10)
        assert result == [1]

    def test_multiple_numbers(self):
        result = parse_selection("1,3,5", 10)
        assert result == [1, 3, 5]

    def test_out_of_range_ignored(self):
        result = parse_selection("1,999,5", 10)
        assert result == [1, 5]

    def test_non_digit_ignored(self):
        result = parse_selection("1,a,5", 10)
        assert result == [1, 5]

    def test_empty_string(self):
        result = parse_selection("", 10)
        assert result == []

    def test_whitespace_handling(self):
        result = parse_selection(" 1 , 3 , 5 ", 10)
        assert result == [1, 3, 5]


class TestPromptYesNo:
    """Test prompt_yes_no function."""

    @patch("sessionintent.app.setup.input", return_value="y")
    def test_yes_returns_true(self, mock_input):
        assert prompt_yes_no("Test?") is True

    @patch("sessionintent.app.setup.input", return_value="Y")
    def test_capital_yes_returns_true(self, mock_input):
        assert prompt_yes_no("Test?") is True

    @patch("sessionintent.app.setup.input", return_value="")
    def test_empty_returns_true(self, mock_input):
        assert prompt_yes_no("Test?") is True

    @patch("sessionintent.app.setup.input", return_value="n")
    def test_no_returns_false(self, mock_input):
        assert prompt_yes_no("Test?") is False

    @patch("sessionintent.app.setup.input", return_value="no")
    def test_no_word_returns_false(self, mock_input):
        assert prompt_yes_no("Test?") is False


class TestSelectAppsOption:
    """Test select_apps_option function."""

    @patch("sessionintent.app.setup.input", return_value="1")
    def test_option_1(self, mock_input):
        assert select_apps_option() == 1

    @patch("sessionintent.app.setup.input", return_value="2")
    def test_option_2(self, mock_input):
        assert select_apps_option() == 2

    @patch("sessionintent.app.setup.input", return_value="3")
    def test_option_3(self, mock_input):
        assert select_apps_option() == 3

    @patch("sessionintent.app.setup.input", side_effect=["invalid", "2"])
    def test_invalid_then_valid(self, mock_input):
        assert select_apps_option() == 2


class TestSelectCategories:
    """Test category selection."""

    def test_category_selection_filters_apps(self):
        mock_apps = {
            "firefox": {"cmd": ["firefox"], "_category": "Browsers"},
            "chrome": {"cmd": ["chrome"], "_category": "Browsers"},
            "vscode": {"cmd": ["code"], "_category": "Development"},
            "discord": {"cmd": ["discord"], "_category": "Communication"},
        }

        categorized = get_categorized_apps(mock_apps)

        assert "Browsers" in categorized
        assert "Development" in categorized
        assert "Communication" in categorized
        assert sorted(categorized["Browsers"].keys()) == ["chrome", "firefox"]
        assert sorted(categorized["Development"].keys()) == ["vscode"]
        assert sorted(categorized["Communication"].keys()) == ["discord"]


class TestAppSelectionFullFlow:
    """Test app selection full flow."""

    def test_get_categorized_apps_preserves_structure(self):
        mock_apps = {
            "firefox": {"cmd": ["firefox"], "check": "firefox", "internal_reuse": True, "_category": "Browsers"},
            "vscode": {"cmd": ["code"], "check": "code", "internal_reuse": True, "_category": "Development"},
        }

        categorized = get_categorized_apps(mock_apps)

        assert "Browsers" in categorized
        assert "Development" in categorized
        assert isinstance(categorized["Browsers"], dict)
        assert isinstance(categorized["Development"], dict)

    def test_detected_apps_have_category_key(self):
        mock_apps = {
            "firefox": {"cmd": ["firefox"], "check": "firefox", "_category": "Browsers"},
            "chrome": {"cmd": ["google-chrome"], "check": "chrome", "_category": "Browsers"},
        }

        categorized = get_categorized_apps(mock_apps)
        assert "firefox" in categorized["Browsers"]
        assert "chrome" in categorized["Browsers"]


ZED_DESKTOP = """[Desktop Entry]
Version=1.0
Type=Application
Name=Zed
Exec=zed %U
StartupNotify=true
Categories=Development;IDE;

[Desktop Action NewWorkspace]
Exec=zed --new %U
Name=Open a new workspace
"""

HIDDEN_DESKTOP = """[Desktop Entry]
Type=Application
Name=Secret
Exec=secret
NoDisplay=true
"""

QUOTED_DESKTOP = """[Desktop Entry]
Type=Application
Name=Quoted
Exec="/opt/my app/run" --flag %U
StartupWMClass=quoted-app
"""


class TestSplitExec:
    """Test Exec line splitting."""

    def test_field_codes_dropped_flags_kept(self):
        assert _split_exec("zed %U") == ["zed"]
        assert _split_exec("app --flag %U") == ["app", "--flag"]

    def test_quoted_path_kept_whole(self):
        assert _split_exec('"/opt/my app/run" --flag %U') == [
            "/opt/my app/run",
            "--flag",
        ]

    def test_percent_word_kept(self):
        assert _split_exec("app 100%") == ["app", "100%"]

    def test_mid_token_quotes(self):
        assert _split_exec(
            '/opt/vivaldi/vivaldi "--profile-directory=Profile 2" --app-id=x %U'
        ) == ["/opt/vivaldi/vivaldi", "--profile-directory=Profile 2", "--app-id=x"]

    def test_unbalanced_quotes_stripped(self):
        assert _split_exec('"/broken %U') == ["/broken"]


class TestParseDesktopEntry:
    """Test section-aware .desktop parsing."""

    def test_action_section_ignored(self):
        fields = _parse_desktop_entry(ZED_DESKTOP)
        assert fields["Name"] == "Zed"
        assert fields["Exec"] == "zed %U"

    def test_only_entry_keys_kept(self):
        fields = _parse_desktop_entry(ZED_DESKTOP)
        assert set(fields) <= {
            "Name",
            "Exec",
            "StartupWMClass",
            "StartupNotify",
            "NoDisplay",
            "Hidden",
            "Type",
        }


class TestDetectDesktopApps:
    """Test desktop file detection end to end."""

    def _write(self, tmp_path, name, content):
        d = tmp_path / "apps"
        d.mkdir(exist_ok=True)
        (d / name).write_text(content)
        return d

    def test_zed_key_not_action_name(self, tmp_path):
        d = self._write(tmp_path, "dev.zed.Zed.desktop", ZED_DESKTOP)
        apps = detect_desktop_apps(desktop_dirs=[d])
        assert "zed" in apps
        assert "open-a-new-workspace" not in apps
        assert apps["zed"]["cmd"] == ["zed"]
        assert apps["zed"]["desktop_id"] == "dev.zed.Zed"

    def test_nodisplay_skipped(self, tmp_path):
        d = self._write(tmp_path, "secret.desktop", HIDDEN_DESKTOP)
        assert detect_desktop_apps(desktop_dirs=[d]) == {}

    def test_scheme_handler_only_skipped(self, tmp_path):
        d = self._write(
            tmp_path,
            "handler.desktop",
            "[Desktop Entry]\nType=Application\nName=Proto\n"
            "Exec=proto %u\nMimeType=x-scheme-handler/proto;\n",
        )
        assert detect_desktop_apps(desktop_dirs=[d]) == {}

    def test_mixed_mimetype_kept(self, tmp_path):
        d = self._write(
            tmp_path,
            "mixed.desktop",
            "[Desktop Entry]\nType=Application\nName=Mixed\nExec=mixed\n"
            "MimeType=text/plain;x-scheme-handler/mixed;\n",
        )
        assert "mixed" in detect_desktop_apps(desktop_dirs=[d])

    def test_wm_class_captured(self, tmp_path):
        d = self._write(tmp_path, "quoted.desktop", QUOTED_DESKTOP)
        apps = detect_desktop_apps(desktop_dirs=[d])
        assert apps["quoted"]["cmd"] == ["/opt/my app/run", "--flag"]
        assert apps["quoted"]["wm_class"] == "quoted-app"

    def test_wm_class_falls_back_to_binary(self, tmp_path):
        d = self._write(tmp_path, "dev.zed.Zed.desktop", ZED_DESKTOP)
        apps = detect_desktop_apps(desktop_dirs=[d])
        assert apps["zed"]["wm_class"] == "zed"


class TestAddNewOnly:
    """Test add-only-new detection and append."""

    def _apps_file(self, tmp_path, monkeypatch, content):
        import sessionintent.app.setup as setupmod

        path = tmp_path / "apps.yaml"
        path.write_text(content)
        monkeypatch.setattr(setupmod, "APPS_PATH", path)
        return path

    def test_existing_keys_loaded(self, tmp_path, monkeypatch):
        self._apps_file(
            tmp_path, monkeypatch, "firefox:\n  cmd: ['firefox']\n"
        )
        assert _load_existing_app_keys() == {"firefox"}

    def test_missing_file_empty(self, tmp_path, monkeypatch):
        import sessionintent.app.setup as setupmod

        monkeypatch.setattr(setupmod, "APPS_PATH", tmp_path / "nope.yaml")
        assert _load_existing_app_keys() == set()

    def test_append_under_header_preserves_existing(self, tmp_path, monkeypatch):
        path = self._apps_file(
            tmp_path,
            monkeypatch,
            "# Development\nzed:\n  cmd: ['zed']\n  check: 'zed'\n",
        )
        added = append_new_apps(
            {"vscode": {"cmd": ["code"], "check": "code"}},
            ["Development", "Other"],
        )
        assert added == 1
        text = path.read_text()
        assert "zed:\n  cmd: ['zed']" in text
        assert "vscode:\n  cmd: ['code']" in text
        assert text.index("zed:") < text.index("vscode:")

    def test_append_creates_missing_header(self, tmp_path, monkeypatch):
        path = self._apps_file(tmp_path, monkeypatch, "zed:\n  cmd: ['zed']\n")
        added = append_new_apps(
            {"steam": {"cmd": ["steam"], "check": "steam"}}, ["Games"]
        )
        assert added == 1
        text = path.read_text()
        assert "# Games\nsteam:" in text

    @patch("sessionintent.app.setup.input", return_value="y")
    def test_add_new_only_bulk(self, mock_input, tmp_path, monkeypatch, capsys):
        self._apps_file(tmp_path, monkeypatch, "zed:\n  cmd: ['zed']\n")
        _add_new_only(
            {
                "zed": {"cmd": ["zed"]},
                "zen": {"cmd": ["flatpak", "run", "app.zen_browser.zen"]},
            }
        )
        out = capsys.readouterr().out
        assert "1 new applications" in out
        assert "zen" in out


class TestDpkgFilter:
    """Test dpkg detector name handling."""

    def _dpkg(self, stdout):
        from unittest.mock import MagicMock

        with (
            patch("sessionintent.app.detect.subprocess.run") as mock_run,
            patch("sessionintent.app.detect.shutil.which") as mock_which,
        ):
            mock_run.return_value = MagicMock(stdout=stdout)
            mock_which.side_effect = lambda exe: f"/usr/bin/{exe}"
            from sessionintent.app.detect import detect_dpkg_apps

            return detect_dpkg_apps()

    def test_dash_names_accepted_arch_stripped(self):
        apps = self._dpkg("ii  my-app:amd64 1.0 desc\nii  ok_tool 2.0 desc\n")
        assert "my-app" in apps
        assert apps["my-app"]["cmd"] == ["my-app"]

    def test_missing_binary_skipped(self):
        from unittest.mock import MagicMock

        with (
            patch("sessionintent.app.detect.subprocess.run") as mock_run,
            patch("sessionintent.app.detect.shutil.which",
                  return_value=None),
        ):
            mock_run.return_value = MagicMock(stdout="ii  ghost 1.0 x\n")
            from sessionintent.app.detect import detect_dpkg_apps

            assert detect_dpkg_apps() == {}


class TestLocalBinApps:
    """Test ~/.local/bin executable detection."""

    def _bindir(self, tmp_path):
        d = tmp_path / "bin"
        d.mkdir()
        exe = d / "claude"
        exe.write_text("#!/bin/sh\nexec foo\n")
        exe.chmod(0o755)
        (d / "notes.txt").write_text("not executable")
        sub = d / "subdir"
        sub.mkdir()
        (d / ".hidden").write_text("x")
        (d / ".hidden").chmod(0o755)
        return d

    def test_executables_only(self, tmp_path):
        apps = detect_local_bin_apps(bin_dirs=[self._bindir(tmp_path)])
        assert list(apps) == ["claude"]
        assert apps["claude"]["cmd"] == [
            str(tmp_path / "bin" / "claude")
        ]
        assert apps["claude"]["check"] == "claude"

    def test_missing_dir_empty(self, tmp_path):
        assert detect_local_bin_apps(bin_dirs=[tmp_path / "nope"]) == {}

    def test_last_priority_wins_for_richer_sources(self):
        with (
            patch(
                "sessionintent.app.detect.detect_flatpak_apps",
                return_value={"dup": {"cmd": ["flatpak", "run", "x"], "check": "dup"}},
            ),
            patch(
                "sessionintent.app.detect.detect_desktop_apps", return_value={}
            ),
            patch("sessionintent.app.detect.detect_dpkg_apps", return_value={}),
            patch("sessionintent.app.detect.detect_rpm_apps", return_value={}),
            patch(
                "sessionintent.app.detect.detect_local_bin_apps",
                return_value={"dup": {"cmd": ["/x/dup"], "check": "dup"}},
            ),
        ):
            apps = detect_all_apps(use_cache=False)
        assert apps["dup"]["cmd"] == ["flatpak", "run", "x"]