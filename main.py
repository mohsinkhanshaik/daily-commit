"""daily-commit: a small Python starter script."""

from datetime import date, datetime

__version__ = "0.1.0"


def time_of_day() -> str:
    """Return a greeting word based on the current hour."""
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 18:
        return "Good afternoon"
    return "Good evening"


def build_greeting() -> str:
    """Return the greeting message printed by the script."""
    return time_of_day() + " from daily-commit!"


def main() -> None:
    """Print the greeting and today's date."""
    print(build_greeting())
    print("Committed on " + date.today().isoformat())


if __name__ == "__main__":
    main()
    
