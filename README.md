# Aare Temp Menubar

Live Aare river water temperature in your macOS menubar.

## Install

### Homebrew (recommended)

```bash
brew tap jl115/aare
brew install --cask aare-temp-menubar
```

> **Note:** The app is ad-hoc signed. macOS may show a security warning on first launch. Right-click the app in Finder and choose **Open** to bypass it.

### Developer (uv)

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
