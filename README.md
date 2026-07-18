# daily-commit

A small Python starter project that prints a time-of-day greeting and today's date.

## Usage

Run the script with Python 3:

```bash
python main.py
```

This prints a greeting based on the current time of day (morning, afternoon, or evening) followed by today's date.

### CLI Options

Use `--name` to personalize the greeting:

```bash
python main.py --name Alice
```

Output: `Good morning, Alice, from daily-commit!`

### Configuration File

Create a `config.json` next to `main.py` to set defaults:

```json
{
  "name": "Alice",
  "language": "es"
}
```

CLI arguments override config file values.

### Supported Languages

Set the `language` key in `config.json` to change the greeting language:

| Code | Language |
|------|----------|
| `en` | English (default) |
| `es` | Spanish |
| `fr` | French |
