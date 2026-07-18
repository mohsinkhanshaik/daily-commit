# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [0.1.0] - 2026-07-17

### Added

- Core greeting script (`main.py`) with `build_greeting` and `main` functions
- `__main__` guard for safe imports
- Module and function docstrings
- Type hints throughout `main.py`
- `__version__` string (`0.1.0`)
- Time-of-day greetings (morning, afternoon, evening)
- Multilingual greeting support (English, Spanish, French)
- `argparse` CLI with `--name` option
- Input validation for CLI arguments
- Logging via the `logging` module
- `constants.py` module for shared constants
- Unit tests in `tests/test_main.py` for `build_greeting`
- Tests covering time-of-day logic
- Optional config file support (`config.json`)
- `.gitignore` for Python artifacts
- `ROADMAP.md` with project improvement checklist
