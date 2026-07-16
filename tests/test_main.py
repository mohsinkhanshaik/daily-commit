"""Unit tests for main.py: build_greeting and time_of_day."""

import unittest
from datetime import datetime
from unittest.mock import patch

from main import build_greeting, time_of_day, GREETINGS


class TestBuildGreeting(unittest.TestCase):
    """Tests for build_greeting with mocked time_of_day."""

    @patch("main.time_of_day", return_value="Good morning")
    def test_greeting_without_name(self, mock_tod):
        result = build_greeting()
        self.assertEqual(result, "Good morning from daily-commit!")
        mock_tod.assert_called_once()

    @patch("main.time_of_day", return_value="Good morning")
    def test_greeting_with_name(self, mock_tod):
        result = build_greeting("Alice")
        self.assertEqual(result, "Good morning, Alice, from daily-commit!")

    @patch("main.time_of_day", return_value="Good afternoon")
    def test_greeting_afternoon(self, mock_tod):
        result = build_greeting()
        self.assertEqual(result, "Good afternoon from daily-commit!")

    @patch("main.time_of_day", return_value="Good evening")
    def test_greeting_evening_with_name(self, mock_tod):
        result = build_greeting("Bob")
        self.assertEqual(result, "Good evening, Bob, from daily-commit!")

    @patch("main.time_of_day", return_value="Good morning")
    def test_greeting_empty_string_name(self, mock_tod):
        result = build_greeting("")
        self.assertEqual(result, "Good morning from daily-commit!")


class TestTimeOfDay(unittest.TestCase):
    """Tests for time_of_day with patched datetime.now."""

    def _call_at_hour(self, hour):
        """Helper: call time_of_day with datetime.now returning the given hour."""
        fake_now = datetime(2026, 1, 1, hour, 0, 0)
        with patch("main.datetime") as mock_dt:
            mock_dt.now.return_value = fake_now
            return time_of_day()

    @patch("main.LANGUAGE", "en")
    def test_morning_english(self):
        self.assertEqual(self._call_at_hour(8), "Good morning")

    @patch("main.LANGUAGE", "en")
    def test_afternoon_english(self):
        self.assertEqual(self._call_at_hour(14), "Good afternoon")

    @patch("main.LANGUAGE", "en")
    def test_evening_english(self):
        self.assertEqual(self._call_at_hour(20), "Good evening")

    @patch("main.LANGUAGE", "en")
    def test_midnight_is_morning(self):
        self.assertEqual(self._call_at_hour(0), "Good morning")

    @patch("main.LANGUAGE", "en")
    def test_noon_is_afternoon(self):
        self.assertEqual(self._call_at_hour(12), "Good afternoon")

    @patch("main.LANGUAGE", "en")
    def test_six_pm_is_evening(self):
        self.assertEqual(self._call_at_hour(18), "Good evening")

    @patch("main.LANGUAGE", "es")
    def test_morning_spanish(self):
        self.assertEqual(self._call_at_hour(9), "Buenos días")

    @patch("main.LANGUAGE", "fr")
    def test_evening_french(self):
        self.assertEqual(self._call_at_hour(21), "Bonsoir")


if __name__ == "__main__":
    unittest.main()
