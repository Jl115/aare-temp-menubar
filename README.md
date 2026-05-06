# Aare Temp Menubar

Live Aare river water temperature in your macOS menubar.

## Install

Requires [uv](https://github.com/astral-sh/uv):

```bash
uv sync
```

## Run

```bash
uv run python -m aare_menubar
```

Or after installing the wheel:

```bash
aare-menubar
```

## Settings

- **Location** — choose city along the Aare
- **Unit** — °C or °F
- **Refresh Interval** — 1, 5, 10, 15, or 30 minutes

## Data

Powered by [Aare.guru API](https://aareguru.existenz.ch/).
