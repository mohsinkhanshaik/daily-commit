"""daily-commit: a small Python starter script."""

from datetime import date

__version__ = "0.1.0"


def build_greeting() -> str:
    """Return the greeting message printed by the script."""
    return "Hello from daily-commit!"


def main() -> None:
    """Print the greeting and today's date."""
    print(build_greeting())
    print("Committed on " + date.today().isoformat())


if __name__ == "__main__":
    main()
