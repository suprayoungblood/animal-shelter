"""Helper script — pre-populates the GUI with sample kennels for the screenshot.

Not part of the app itself. Run with:
    python3 scripts/capture_screenshots.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from animals import Bird, Cat, Dog  # noqa: E402
from gui.app import AnimalShelterApp  # noqa: E402


def main() -> None:
    """Launch the GUI with three sample kennels already added."""
    app = AnimalShelterApp()
    app._handle_add(Dog("Rex", 4, "Labrador"))
    app._handle_add(Cat("Whiskers", 2, "Black"))
    app._handle_add(Bird("Tweety", 1, 6.5))
    app.mainloop()


if __name__ == "__main__":
    main()
