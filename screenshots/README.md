# Screenshots

This folder holds the two PNGs referenced by the main README:

| Filename            | What it shows                                                       |
| ------------------- | ------------------------------------------------------------------- |
| `app_running.png`   | The Tkinter GUI with three sample kennels (Dog, Cat, Bird) added   |
| `code_view.png`     | An editor-style panel of `dog.py`, `kennel.py`, and `gui/app.py`    |

## Regenerating

```bash
# GUI window — launch with sample data, then capture the window:
python3 scripts/capture_screenshots.py
# Cmd + Shift + 4, then Space, then click the window

# Code panel — re-rendered programmatically:
python3 scripts/render_code_image.py
```

**Capture tips for `app_running.png`**

- Hide the browser bookmark bar and notifications/cloud icons before capture.
- On macOS: `Cmd + Shift + 4` then press `Space` to capture a single window
  cleanly without the desktop background.
