"""Unit tests for the build_greeting function in main.py."""

import unittest
from unittest.mock import patch

from main import build_greeting


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
                                                                                                                                    
                                                                                                                                    
                                                                                                                                    if __name__ == "__main__":
                                                                                                                                        unittest.main()
                                                                                                                                        
