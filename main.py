"""daily-commit: a small Python starter script."""

from datetime import date, datetime

__version__ = "0.1.0"

# Language code used for greetings. Supported: "en", "es", "fr".
LANGUAGE = "en"

# Time-of-day greetings per language: (morning, afternoon, evening).
GREETINGS = {
    "en": ("Good morning", "Good afternoon", "Good evening"),
    "es": ("Buenos días", "Buenas tardes", "Buenas noches"),
    "fr": ("Bonjour", "Bon après-midi", "Bonsoir"),
}


def time_of_day() -> str:
    """Return a greeting for the current hour in the LANGUAGE language."""
    morning, afternoon, evening = GREETINGS.get(LANGUAGE, GREETINGS["en"])
    hour = datetime.now().hour
    if hour < 12:
        return morning
    if hour < 18:
        return afternoon
    return evening


def build_greeting() -> str:
    """Return the greeting message printed by the script."""
    return time_of_day() + " from daily-commit!"


def main() -> None:
    """Print the greeting and today's date."""
    print(build_greeting())
    print("Committed on " + date.today().isoformat())


if __name__ == "__main__":
    main()
