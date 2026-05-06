"""Entry point."""
from .app import AareMenubarApp


def main() -> None:
    app = AareMenubarApp()
    app.run()


if __name__ == "__main__":
    main()
