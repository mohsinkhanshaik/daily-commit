"""daily-commit: a small Python starter script."""

from datetime import date


def build_greeting():
    """Return the greeting message printed by the script."""
    return "Hello from daily-commit!"


def main():
    """Print the greeting and today's date."""
    print(build_greeting())
    print("Committed on " + date.today().isoformat())


if __name__ == "__main__":
    main()
