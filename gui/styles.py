"""Centralized theme: colors, fonts, and ttk style configuration.

Single source of truth — every widget pulls from here so look-and-feel changes
happen in one place.
"""
from tkinter import ttk

PALETTE = {
    "bg":        "#0f172a",  # slate-900
    "panel":     "#1e293b",  # slate-800
    "panel_alt": "#334155",  # slate-700
    "accent":    "#38bdf8",  # sky-400
    "accent_hi": "#0ea5e9",  # sky-500
    "success":   "#22c55e",  # green-500
    "danger":    "#ef4444",  # red-500
    "text":      "#f1f5f9",  # slate-100
    "muted":     "#94a3b8",  # slate-400
}

FONTS = {
    "title":  ("SF Pro Display", 22, "bold"),
    "h2":     ("SF Pro Display", 14, "bold"),
    "body":   ("SF Pro Text", 12),
    "small":  ("SF Pro Text", 10),
    "button": ("SF Pro Text", 12, "bold"),
}

WINDOW_SIZE = "960x600"
PAD = 12


def apply_theme(root) -> None:
    """Apply the dark theme to the root window and all ttk widgets."""
    root.configure(bg=PALETTE["bg"])
    style = ttk.Style(root)
    style.theme_use("clam")
    _style_frames(style)
    _style_labels(style)
    _style_inputs(style)
    _style_buttons(style)
    _style_treeview(style)


def _style_frames(style: ttk.Style) -> None:
    """Style frame containers."""
    style.configure("App.TFrame", background=PALETTE["bg"])
    style.configure("Panel.TFrame", background=PALETTE["panel"])
    style.configure(
        "Card.TLabelframe",
        background=PALETTE["panel"],
        foreground=PALETTE["text"],
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "Card.TLabelframe.Label",
        background=PALETTE["panel"],
        foreground=PALETTE["accent"],
        font=FONTS["h2"],
    )


def _style_labels(style: ttk.Style) -> None:
    """Style text labels."""
    style.configure(
        "Title.TLabel",
        background=PALETTE["bg"],
        foreground=PALETTE["text"],
        font=FONTS["title"],
    )
    style.configure(
        "Subtitle.TLabel",
        background=PALETTE["bg"],
        foreground=PALETTE["muted"],
        font=FONTS["small"],
    )
    style.configure(
        "Field.TLabel",
        background=PALETTE["panel"],
        foreground=PALETTE["text"],
        font=FONTS["body"],
    )
    style.configure(
        "Status.TLabel",
        background=PALETTE["panel_alt"],
        foreground=PALETTE["text"],
        font=FONTS["small"],
        padding=6,
    )


def _style_inputs(style: ttk.Style) -> None:
    """Style entry and combobox widgets."""
    style.configure(
        "TEntry",
        fieldbackground=PALETTE["panel_alt"],
        foreground=PALETTE["text"],
        insertcolor=PALETTE["text"],
        bordercolor=PALETTE["panel_alt"],
        lightcolor=PALETTE["panel_alt"],
        darkcolor=PALETTE["panel_alt"],
        padding=6,
    )
    style.configure(
        "TCombobox",
        fieldbackground=PALETTE["panel_alt"],
        background=PALETTE["panel_alt"],
        foreground=PALETTE["text"],
        arrowcolor=PALETTE["text"],
        padding=6,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", PALETTE["panel_alt"])],
        foreground=[("readonly", PALETTE["text"])],
    )


def _style_buttons(style: ttk.Style) -> None:
    """Style primary and danger buttons."""
    style.configure(
        "Accent.TButton",
        background=PALETTE["accent"],
        foreground=PALETTE["bg"],
        font=FONTS["button"],
        borderwidth=0,
        padding=(16, 8),
    )
    style.map(
        "Accent.TButton",
        background=[("active", PALETTE["accent_hi"])],
    )
    style.configure(
        "Danger.TButton",
        background=PALETTE["danger"],
        foreground=PALETTE["text"],
        font=FONTS["button"],
        borderwidth=0,
        padding=(16, 8),
    )
    style.map(
        "Danger.TButton",
        background=[("active", "#b91c1c")],
    )


def _style_treeview(style: ttk.Style) -> None:
    """Style the kennel list Treeview."""
    style.configure(
        "Kennel.Treeview",
        background=PALETTE["panel_alt"],
        fieldbackground=PALETTE["panel_alt"],
        foreground=PALETTE["text"],
        rowheight=28,
        borderwidth=0,
        font=FONTS["body"],
    )
    style.configure(
        "Kennel.Treeview.Heading",
        background=PALETTE["panel"],
        foreground=PALETTE["accent"],
        font=FONTS["button"],
        borderwidth=0,
        padding=6,
    )
    style.map(
        "Kennel.Treeview",
        background=[("selected", PALETTE["accent_hi"])],
        foreground=[("selected", PALETTE["bg"])],
    )
