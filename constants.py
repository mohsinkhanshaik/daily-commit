"""Shared constants for the daily-commit project."""

# Project version.
VERSION = "0.1.0"

# Language code used for greetings. Supported: "en", "es", "fr".
LANGUAGE = "en"

# Time-of-day greetings per language: (morning, afternoon, evening).
GREETINGS = {
    "en": ("Good morning", "Good afternoon", "Good evening"),
    "es": ("Buenos dias", "Buenas tardes", "Buenas noches"),
    "fr": ("Bonjour", "Bon apres-midi", "Bonsoir"),
}

# Logging format string.
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
