"""Launch the GUI, pre-populate it, and screenshot ONLY the app window.

Captures the exact window region (with the window raised to the front) so no
desktop, dock, menu bar, browser bookmarks, or other apps appear in the image.

Output: ~/Desktop/Animal_Shelter_Simulator/Application/02_gui_front_end.png

Run with:
    python3 scripts/capture_gui.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from animals import Bird, Cat, Dog  # noqa: E402
from gui.app import AnimalShelterApp  # noqa: E402

OUT = (
    Path.home()
    / "Desktop"
    / "Animal_Shelter_Simulator"
    / "Application"
    / "02_gui_front_end.png"
)


def _shoot(app: AnimalShelterApp) -> None:
    """Capture only the window's region, then close the app."""
    app.update_idletasks()
    app.update()
    x = app.winfo_rootx()
    y = app.winfo_rooty()
    w = app.winfo_width()
    h = app.winfo_height()
    # Include the title bar by extending upward a little; clamp at 0.
    title_bar = 28
    region = f"{x},{max(y - title_bar, 0)},{w},{h + title_bar}"
    subprocess.run(["screencapture", "-x", "-R", region, str(OUT)], check=False)
    print(f"Saved {OUT} (region {region})")
    app.destroy()


def main() -> None:
    app = AnimalShelterApp()
    # Populate every panel: housed animals, an adoption in the log,
    # and a waiting-list entry.
    app._handle_add(Dog("Charlie", 7, "Golden Retriever"))
    app._handle_add(Cat("Luna", 5, "Orange Tabby"))
    app._handle_add(Bird("Tweety", 1, 6.5))
    app._handle_adopt("Cat", "Avery")
    app._handle_add(Dog("Rex", 3, "Beagle"))
    app._handle_adopt("Cat", "Blake")
    app.geometry("980x640+120+120")
    app.update()
    app.lift()
    app.attributes("-topmost", True)
    # Give the window manager time to draw, then shoot.
    app.after(900, lambda: _shoot(app))
    app.mainloop()


if __name__ == "__main__":
    main()
