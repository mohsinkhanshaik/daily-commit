"""daily-commit: a small Python starter script."""

import argparse
import json
import logging
import os
import sys
from datetime import date, datetime
from typing import Optional

__version__ = "0.1.0"

# Configure module-level logger.
logger = logging.getLogger(__name__)

# Language code used for greetings. Supported: "en", "es", "fr".
LANGUAGE = "en"

# Time-of-day greetings per language: (morning, afternoon, evening).
GREETINGS = {
    "en": ("Good morning", "Good afternoon", "Good evening"),
    "es": ("Buenos días", "Buenas tardes", "Buenas noches"),
    "fr": ("Bonjour", "Bon après-midi", "Bonsoir"),
}


def load_config() -> dict:
    """Load optional settings from config.json if it exists next to this script."""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    if os.path.isfile(config_path):
        try:
            with open(config_path, encoding="utf-8") as fh:
                config = json.load(fh)
            logger.info("Loaded config from %s", config_path)
            return config
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not load config.json: %s", exc)
    return {}


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
    logger.debug("Current hour: %d, language: %s", hour, LANGUAGE)
    if hour < 12:
        return morning
    if hour < 18:
        return afternoon
    return evening


def build_greeting(name: Optional[str] = None) -> str:
    """Return the greeting message printed by the script."""
    greeting = time_of_day()
    if name:
        result = f"{greeting}, {name}, from daily-commit!"
    else:
        result = greeting + " from daily-commit!"
    logger.info("Generated greeting: %s", result)
    return result


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
    global LANGUAGE
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger.info("Starting daily-commit v%s", __version__)

    # Load optional config file.
    config = load_config()
    if "language" in config:
        LANGUAGE = config["language"]

    try:
        args = parse_args()
        name = args.name or config.get("name")
        print(build_greeting(name))
        print("Committed on " + date.today().isoformat())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:
        logger.error("Unhandled error: %s", exc)
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
