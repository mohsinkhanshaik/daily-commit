"""daily-commit: a small Python starter script."""

import argparse
import sys
from datetime import date, datetime
from typing import Optional

__version__ = "0.1.0"

# Language code used for greetings. Supported: "en", "es", "fr".
LANGUAGE = "en"

# Time-of-day greetings per language: (morning, afternoon, evening).
GREETINGS = {
    "en": ("Good morning", "Good afternoon", "Good evening"),
    "es": ("Buenos días", "Buenas tardes", "Buenas noches"),
    "fr": ("Bonjour", "Bon après-midi", "Bonsoir"),
}


def validate_name(name: str) -> str:
    """Validate the --name argument is not empty or whitespace-only."""
    stripped = name.strip()
    if not stripped:
        raise argparse.ArgumentTypeError("name must not be empty or whitespace-only")
    return stripped


def time_of_day() -> str:
    """Return a greeting for the current hour in the LANGUAGE language."""
    morning, afternoon, evening = GREETINGS.get(LANGUAGE, GREETINGS["en"])
    hour = datetime.now().hour
    if hour < 12:
        return morning
    if hour < 18:
        return afternoon
    return evening


def build_greeting(name: Optional[str] = None) -> str:
    """Return the greeting message printed by the script."""
    if name:
        return f"{time_of_day()}, {name}, from daily-commit!"
    return time_of_day() + " from daily-commit!"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the script."""
    parser = argparse.ArgumentParser(
        description="Print a time-of-day greeting and today's date."
    )
    parser.add_argument(
        "--name", type=validate_name, help="name to include in the greeting"
    )
    return parser.parse_args()


def main() -> None:
    """Print the greeting and today's date."""
    try:
        args = parse_args()
        print(build_greeting(args.name))
        print("Committed on " + date.today().isoformat())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
