"""
Tests for SessionIntent app detection and setup.
"""

from unittest.mock import patch

from src.app.detect import (
    categorize_app,
    get_category_list,
    get_categorized_apps,
)
from src.app.setup import (
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
        assert categorize_app("discord") == "Media & Entertainment"

    def test_categorize_spotify(self):
        assert categorize_app("spotify") == "Media & Entertainment"

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

    def test_returns_seven_categories(self):
        categories = get_category_list()
        assert len(categories) == 7

    def test_first_category_is_browsers(self):
        categories = get_category_list()
        assert categories[0] == ("Browsers", 1)

    def test_categories_have_numbers(self):
        categories = get_category_list()
        for cat, num in categories:
            assert isinstance(cat, str)
            assert isinstance(num, int)
            assert 1 <= num <= 7

    def test_last_category_is_other(self):
        categories = get_category_list()
        assert categories[-1] == ("Other", 7)


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

    @patch("src.app.setup.input", return_value="y")
    def test_yes_returns_true(self, mock_input):
        assert prompt_yes_no("Test?") is True

    @patch("src.app.setup.input", return_value="Y")
    def test_capital_yes_returns_true(self, mock_input):
        assert prompt_yes_no("Test?") is True

    @patch("src.app.setup.input", return_value="")
    def test_empty_returns_true(self, mock_input):
        assert prompt_yes_no("Test?") is True

    @patch("src.app.setup.input", return_value="n")
    def test_no_returns_false(self, mock_input):
        assert prompt_yes_no("Test?") is False

    @patch("src.app.setup.input", return_value="no")
    def test_no_word_returns_false(self, mock_input):
        assert prompt_yes_no("Test?") is False


class TestSelectAppsOption:
    """Test select_apps_option function."""

    @patch("src.app.setup.input", return_value="1")
    def test_option_1(self, mock_input):
        assert select_apps_option() == 1

    @patch("src.app.setup.input", return_value="2")
    def test_option_2(self, mock_input):
        assert select_apps_option() == 2

    @patch("src.app.setup.input", return_value="3")
    def test_option_3(self, mock_input):
        assert select_apps_option() == 3

    @patch("src.app.setup.input", side_effect=["invalid", "2"])
    def test_invalid_then_valid(self, mock_input):
        assert select_apps_option() == 2


class TestSelectCategories:
    """Test category selection."""

    def test_category_selection_filters_apps(self):
        mock_apps = {
            "firefox": {"cmd": ["firefox"], "_category": "Browsers"},
            "chrome": {"cmd": ["chrome"], "_category": "Browsers"},
            "vscode": {"cmd": ["code"], "_category": "Development"},
            "discord": {"cmd": ["discord"], "_category": "Media & Entertainment"},
        }

        categorized = get_categorized_apps(mock_apps)

        assert "Browsers" in categorized
        assert "Development" in categorized
        assert "Media & Entertainment" in categorized
        assert sorted(categorized["Browsers"].keys()) == ["chrome", "firefox"]
        assert sorted(categorized["Development"].keys()) == ["vscode"]
        assert sorted(categorized["Media & Entertainment"].keys()) == ["discord"]


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